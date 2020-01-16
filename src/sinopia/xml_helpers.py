__author__ = "Jeremy Nelson"

import datetime
import io
import rdflib
import requests
import pymarc
import uuid
import sys
from lxml import etree

BF = rdflib.Namespace("http://id.loc.gov/ontologies/bibframe/")
BFLC = rdflib.Namespace("http://id.loc.gov/ontologies/bflc/")
SINOPIA = rdflib.Namespace("http://sinopia.io/vocabulary/")
XML_NS = {"bf": "http://id.loc.gov/ontologies/bibframe/", 
          "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}

# Function Opens the XSLT filepath as a file and returns an lxml XSLT object
def get_xslt(filepath):
    with open(filepath, "rb") as fo:
        xml = etree.XML(fo.read())
    return etree.XSLT(xml)

# Function binds three of the specific RDF namespaces used by Sinopia.
def init_ns(graph):
    graph.namespace_manager.bind("bf", BF)
    graph.namespace_manager.bind("bflc", BFLC)
    graph.namespace_manager.bind("sinopia", SINOPIA)
    
# Function takes a graph, serializes to XML, and the returns the transformed MARC XML
def graph2marcXML(graph):
    rdf_xml = etree.XML(graph.serialize(format='pretty-xml'))
    try:
        return bf2marc_transform(rdf_xml)
    except:
        print(f"Error transforming graph to {sys.exc_info()[0]}")
    
# Function takes a list of Sinopia URLs, creates graphs for each, serializes to XML before, combining
# back into a single XML document for transformation 
def graph2RDFXML(uris):
    for uri in uris:
        graph = triples2record(uri)
        rdf_xml = etree.XML(graph.serialize(format='pretty-xml'))
        yield rdf_xml

# Function takes a MARC XML document and returns the MARC 21 equalivant
def marcXMLto21(marcXML):
    reader = io.StringIO(etree.tostring(marcXML).decode())
    marc_records = pymarc.parse_xml_to_array(reader)
    # Should only be 1 record in the list
    return marc_records[0]

# Function takes a list Sinopia URIs and returns a RDF Graph
def triples2record(uris):
    record_graph = rdflib.Graph()
    init_ns(record_graph)
    for uri in uris:
        get_request = requests.get(uri)
        raw_utf8 = get_request.text.encode(get_request.encoding).decode()
        record_graph.parse(data=raw_utf8, format='turtle')
    return record_graph

   
# Function takes a Sinopia URI that has a relative URI, replaces relative with absolute, and returns 
# new graph
def update_abs_url(uri):
    get_request = requests.get(uri)
    raw_utf8 = get_request.text.encode(get_request.encoding).decode()
    raw_utf8 = raw_utf8.replace('<>', f"<{uri}>")
    graph = rdflib.Graph()
    init_ns(graph)
    graph.parse(data=raw_utf8, format='turtle')
    return graph

# Function takes a bf:Instance and a bf:Work and constructs a combined XML document with both of these 
# entities as top-level XML elements
def unnestedXML(instance_uri, work_uri):
  instance = triples2record([instance_uri])
  work = triples2record([work_uri])
  # Use the instance XML as the record xml base
  record_xml = etree.XML(instance.serialize(format='pretty-xml'))
  work_xml = etree.XML(work.serialize(format='pretty-xml'))
  work_element = work_xml.find("bf:Work", XML_NS)
  for child in work_xml.iterchildren():
    record_xml.append(child)
  return record_xml

# Function takes a graph with a URI bf:Work with a nested bf:Instance serializes the output to XML and then modifies 
# XML with the expected structure for the bibframe2marc transformation
def nestedInstance(incoming_rdf):
    if isinstance(incoming_rdf, rdflib.Graph) or isinstance(incoming_rdf, rdflib.ConjunctiveGraph):
    	rdf_xml = etree.XML(incoming_rdf.serialize(format='pretty-xml'))
    else:
        rdf_xml = incoming_rdf
    hasInstance = rdf_xml.find("bf:Work/bf:hasInstance", XML_NS)
    bfInstance = hasInstance.find("bf:Instance", XML_NS)
    # Delete the instance from the hasInstance element
    hasInstance.remove(bfInstance)
    # Creates relationship betweemn bf:hasInstance and the instance
    if len(hasInstance.attrib) < 1:
        bfInstance.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}nodeID"] = str(uuid.uuid1())
    node_id = bfInstance.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}nodeID"]
    hasInstance.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"] = node_id
    # Adds rdf:about to bfInstance
    bfInstance.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"] = node_id
    # Adds the instance back as a top-level element
    if hasattr(rdf_xml, 'getroot'):
        rdf_xml.getroot().append(bfInstance)
    else:
        rdf_xml.append(bfInstance)
    return rdf_xml

# Function takea a graph with an bf:Instance with one or more nested bf:Works, serializes to XML and then modifies
# the XML to the expected structure for the bibframe2marc xslt
def nestedWork(graph):
    rdf_xml = etree.XML(graph.serialize(format='pretty-xml'))
    instanceOfs = rdf_xml.findall("bf:instanceOf", XML_NS)
    for elem in instanceOfs:
        bfWork = elem.find("bf:Work", XML_NS)
        work_node_id = bfWork.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}nodeID"]
        elem.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"] = work_node_id
        elem.remove(bfWork)
        rdf_xml.append(bfWOrk)
    return rdf_xml


