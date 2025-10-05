#!/usr/bin/env python
from lxml import etree
import sys

def pretty_print_xml(input_file, output_file):
    # Parse the XML file
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_file, parser)
    
    # Pretty print the XML
    pretty_xml_as_string = etree.tostring(tree, pretty_print=True, encoding='unicode')
    
    # Write the pretty XML to the output file
    with open(output_file, 'w') as f:
        f.write(pretty_xml_as_string)

# works with GraphML, chokes on GML
pretty_print_xml(sys.argv[1], "pretty_" + sys.argv[1])
