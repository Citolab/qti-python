import xml.etree.ElementTree as ET
import zipfile
import os
import csv
import subprocess
from helpers.qti_model import alternative, multiple_choice_item, interaction_type, item_base
from helpers.helper_functions import clean, get_namespace, get_correct_tag, get_interaction_type, get_item_resource_type, get_end_clean, is_child_of

FILE_NAME = '/Users/marcelh/Downloads/packages_4a1bc6363ddd8894211669eaef2b52d4262a94f6498b6a0f841a3f6c93255f78_QTI toets Toets 1.1.1 NL GB 05-10-2022_qti3.zip'
TEMP_FOLDER = '/Users/marcelh/Downloads/temp'

if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

PACKAGE_FOLDER = TEMP_FOLDER + '/package'

zip_ref = zipfile.ZipFile(FILE_NAME, 'r')
zip_ref.extractall(PACKAGE_FOLDER)
zip_ref.close()

# open manifest file
manifest = ET.parse(PACKAGE_FOLDER + '/imsmanifest.xml').getroot()
namespace = get_namespace(manifest)

ns = {'d': namespace}
# xpath to get all items in package
items = []
# Find all resources with 'item' in the type attribute using XPath
item_resource_types = get_item_resource_type(manifest, ns)
item_refs = manifest.findall(
    f".//d:resource[@type='{item_resource_types}']", ns)
item_codes = [item_ref.attrib['href'] for item_ref in item_refs]
# loop through all item references
for item_ref in item_codes:
    # open item xml file
    item = ET.parse(PACKAGE_FOLDER + '/' + item_ref).getroot()
    item_namespace = get_namespace(item)
    item_ns = {'d': item_namespace}
    VERSION = 3 if '_v3' in item_namespace else 2
    # get item body
    item_body = item.find(f'.//d:{get_correct_tag(VERSION, "itemBody")}', item_ns)
    interactions = []
    BODY = ''
    item_type = interaction_type.NotDetermined
    alternatives = []
    # loop through elements of item body to get body text and interaction info
    for elem in item_body.findall(".//*"):
        elem_name = elem.tag.replace(
            item_namespace, '')
        if elem_name.lower().endswith('interaction'):
            interactions.append(elem)
            if item_type == '' or item_type == interaction_type.NotDetermined:
                item_type = get_interaction_type(VERSION, elem_name)
                if item_type == interaction_type.Choice:
                    alternatives = [alternative(choice.attrib['identifier'], clean(' '.join([get_end_clean(
                        c_el) for c_el in choice.findall('.//*')]))) for choice in elem.findall(f'.//d:{get_correct_tag(VERSION, "simpleChoice")}', item_ns)]
        else:
            if elem.text is not None and not is_child_of(interactions, elem):
                BODY = BODY + ' ' + clean(elem.text)
            if elem.tail is not None and not is_child_of(interactions, elem):
                BODY = BODY + ' ' + clean(elem.tail)
    BODY = clean(BODY)
    correct_response_element = item.find(f'.//d:{get_correct_tag(VERSION, "correctResponse")}', item_ns)
    res_e = []
    if correct_response_element is not None:
        res_e = [get_end_clean(cr_elem) for cr_elem in correct_response_element.findall('.//*')]
    else:
        res_e = []  # Assign an empty list if no correctResponse element is found
    CORRECT_RESPONSE = '#'.join(res_e)
    base_item = multiple_choice_item(item.attrib['identifier'], item_type, BODY, CORRECT_RESPONSE, alternatives) \
        if item_type == interaction_type.Choice \
        else item_base(item.attrib['identifier'], item_type, BODY, CORRECT_RESPONSE)
    items.append(base_item)
choice_items = [itm for itm in items if itm.interaction_type == interaction_type.Choice]
if len(choice_items) > 0:
    with open('muliple_choice_items.csv', mode='w', encoding="utf-8", newline='') as csv_file:
        # sort on max alternatives so we get the item with max columns
        # sorted_items = choice_items[:]
        sorted_items = sorted(choice_items, key=lambda x: len(x.alternatives), reverse=True)
        # get column headers from item with most alternatives
        fieldnames = sorted_items[0].to_dict().keys()
        writer = csv.DictWriter(
            csv_file, fieldnames=fieldnames,  delimiter=';')
        writer.writeheader()
        for choice in choice_items:
            writer.writerow(choice.to_dict())
# clean temp folder whould work on windows and linux
subprocess.run(['rm', '-rf', TEMP_FOLDER])
print('done')

