import os.path
import requests
import zipfile
import re
import os
from urllib.parse import urlparse, urlencode

#PROXIES_URL = "https://raw.githubusercontent.com/Stefanuk12/RoProPatcher/master/proxies.txt"

def download_chrome_extension(id_or_url, output_file=None, convert_to_zip=True, quiet=False):
    try:
        ext_url = urlparse(id_or_url)
        ext_id = os.path.basename(ext_url.path)
    except:
        ext_id = id_or_url

    crx_base_url = 'https://clients2.google.com/service/update2/crx'
    crx_params = {
        'response': 'redirect',
        'prodversion': '91.0',
        'acceptformat': 'crx2,crx3',
        'x': 'id=' + ext_id + '&uc'
    }
    crx_url = crx_base_url + '?' + urlencode(crx_params)

    if output_file is None:
        output_file = ext_id + '.crx'

    if not quiet:
        print('Downloading {} to {} ...'.format(crx_url, output_file))

    response = requests.get(crx_url)
    response.raise_for_status()

    with open(output_file, 'wb') as file:
        file.write(response.content)

    if not quiet:
        print('Downloaded CRX file.')

    if convert_to_zip:
        crx_to_zip(output_file)

def crx_to_zip(crx_file):
    zip_file = os.path.splitext(crx_file)[0] + '.zip'

    with zipfile.ZipFile(zip_file, 'w') as zipf:
        with zipfile.ZipFile(crx_file, 'r') as crxf:
            for item in crxf.infolist():
                content = crxf.read(item.filename)
                zipf.writestr(item, content)

    print('Converted CRX to ZIP: {}'.format(zip_file))

# def get_proxies():
#     response = requests.get(PROXIES_URL)
#     response.raise_for_status()
#     print(response.text.splitlines())
#     return response.text.splitlines()

def patch(path, proxy):
    re_pattern = re.compile(r"(https://api\.)ropro\.io/(validateUser\.php|getServerInfo\.php|getServerConnectionScore\.php|getServerAge\.php|getSubscription\.php)")
    rep = f"https://{proxy}/$2///api"

    # Patching the background file
    background_path = os.path.join(path, "background.js")
    with open(background_path, "rb") as background_file:
        background_contents = background_file.read().decode('utf-8')

    new_background_contents = re_pattern.sub(rep, background_contents)
    with open(background_path, "wb") as background_file:
        background_file.write(new_background_contents.encode('utf-8'))

    if background_contents == new_background_contents:
        print("Warning: Nothing changed while patching `background.js` (and possibly others within js/page) - already patched?")

    # Patching each file in js/page
    jspage_path = os.path.join(path, "js/page")
    for file_entry in os.listdir(jspage_path):
        file_path = os.path.join(jspage_path, file_entry)
        with open(file_path, "rb") as file:
            file_data = file.read().decode('utf-8')

        new_file_data = re_pattern.sub(rep, file_data)
        with open(file_path, "wb") as file:
            file.write(new_file_data.encode('utf-8'))


def extract_zip(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


#download_chrome_extension('adbacgifemdbhdkfppmeilbgppmhaobf', 'file.crx', True, False)


patch(r'C:\Users\SeanS\PycharmProjects\RoProPatcher\file', 'ropro.darkhub.cloud')