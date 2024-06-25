import re
import unicodedata
import ntpath
import html
import xml.etree.ElementTree as ET
from helpers.qti_model import interaction_type

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_correct_tag(version: int, tag: str):
    if version == 3 and 'qti-' not in tag:
        return camel_to_kebab_prefixed(tag)
    else:
        if 'qti-' in tag:
            return kebab_prefixed_to_camel(tag)
    return tag

def get_interaction_type(version: int, element_name: str):
    switcher = {
        get_correct_tag(version, 'textEntryInteraction'): interaction_type.TextEntry,
        get_correct_tag(version, 'extendedTextInteraction'): interaction_type.ExtendedText,
        get_correct_tag(version, 'choiceInteraction'): interaction_type.Choice
    }
    return switcher.get(element_name.replace('{', '').replace('}', ''), interaction_type.NotDetermined)

def camel_to_kebab_prefixed(camel_case_string):
    # Convert camelCase to kebab-case
    kebab_case_string = re.sub(r'([a-z])([A-Z])', r'\1-\2', camel_case_string).lower()
    # Prefix with 'qti-'
    kebab_case_prefixed = f'qti-{kebab_case_string}'
    return kebab_case_prefixed

def kebab_prefixed_to_camel(kebab_prefixed_string):
    # Remove the 'qti-' prefix
    if kebab_prefixed_string.startswith('qti-'):
        kebab_string = kebab_prefixed_string[4:]
    else:
        return kebab_prefixed_string  # Return as-is if the prefix is not present

    # Convert kebab-case to camelCase
    components = kebab_string.split('-')
    camel_case_string = components[0] + ''.join(x.capitalize() for x in components[1:])
    return camel_case_string

def clean(s):
    if s is not None:
        s = html.unescape(s)
        s = replaceTabSpacesNewLineBySpaces(s)
        s = replaceNewLineBySpaces(s)
        s = removeWeirdSpaces(s)
        s = removeDoubleSpaces(s)
        s = removeDoubleSpaces(s)
        s = s.strip()
        return s
    return ''


def get_end_clean(elem):
    if elem is not None:
        elem_name = elem.tag.replace(
            '{http://www.imsglobal.org/xsd/imsqti_v2p1}', '')
        if elem_name == 'img':
            return path_leaf(elem.attrib['src'])
        else:
            return clean(elem.text)


def removeDoubleSpaces(s):
    return re.sub(' +', ' ', s)


def replaceTabSpacesNewLineBySpaces(s):
    return re.sub(r'\s+', ' ', s)


def replaceNewLineBySpaces(s):
    return s.replace('\n', ' ').replace('\r', '')


def removeWeirdSpaces(s):
    s = unicodedata.normalize("NFKD", s)
    return s

def is_child_of(parents, child):
    for parent in parents:
        for elem in parent.findall(".//*"):
            if elem == child:
                return True
    return False

def get_unique_type_values(manifest, ns):
    # Get all 'type' attribute values from 'resource' elements
    type_values = [resource.get('type') for resource in manifest.findall(".//d:resource", ns)]

    # Get distinct type values
    unique_type_values = list(set(type_values))

    return unique_type_values

def get_item_resource_type(manifest, ns):
    # Get all unique type values
    types = get_unique_type_values(manifest, ns)
    
    # Filter and return values that contain 'item'
    item_types = [t for t in types if 'item' in t]
    return item_types[0] if len(item_types) > 0 else ''


def get_namespace(root, prefix=None):   
    if prefix:
        # Construct the attribute name for the prefixed namespace
        namespace_attr = f"xmlns:{prefix}"
        # Get the prefixed namespace URL from the attributes
        namespace_url = root.attrib.get(namespace_attr)
    else:
        # Get the default namespace from the root element's tag
        namespace_url = root.tag[root.tag.find('{')+1:root.tag.find('}')]
    
    return namespace_url