import logging
import os.path
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote, urljoin

import requests
from loguru import logger
from requests.utils import cookiejar_from_dict
from requests_toolbelt.multipart.encoder import MultipartEncoder

logger.remove()
logger.add(sys.stderr, level=logging.NOTSET,
           format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <level>{level}</level> - <cyan>{name}</cyan> - '
                  '<cyan>{function}</cyan> - <cyan>{line}</cyan> - <level>{message}</level>')


class CsdnBlogUploader:
    def __init__(self, source: str, output_dir: str):
        cookie = 'uuid_tt_dd=10_20283672180-1675681213636-361097; __bid_n=18626622e1b116903f4207; ' \
                 '__gads=ID=1b92ecc37cc46cfc-22b7a5a991d90076:T=1675681213:RT=1675681213:S' \
                 '=ALNI_MZO2IRq1IcjWIFTCRbWcT3dzFIJYw; _ga=GA1.2.560899441.1675681214; UserName=weixin_43701894; ' \
                 'UserInfo=4c9b7933ee604ac4af575fbfeb8c0082; UserToken=4c9b7933ee604ac4af575fbfeb8c0082; ' \
                 'UserNick=weixin_43701894; AU=A55; UN=weixin_43701894; BT=1677070375339; p_uid=U010000; ' \
                 'Hm_up_6bcd52f51e9b3dce32bec4a3997715ac=%7B%22islogin%22%3A%7B%22value%22%3A%221%22%2C%22scope%22' \
                 '%3A1%7D%2C%22isonline%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%2C%22isvip%22%3A%7B' \
                 '%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%22weixin_43701894%22%2C' \
                 '%22scope%22%3A1%7D%7D; _gid=GA1.2.706525915.1678368614; firstDie=1; ' \
                 '__gpi=UID=00000bb6a7cdd736:T=1675681213:RT=1678369392:S=ALNI_MZK6Ket09W9llhZ7ATI_OwUuHLPFw; ' \
                 'ssxmod_itna=Yq0x9Qi=D=3CqYKGHLonBYGOCwP2oqY5E=oYD/GbmDnqD=GFDK40oEBND7mKnanx4a418tpiwxW5FA4ERY=ch' \
                 '+yeDHxY=DUEO0oqbDeW=D5xGoDPxDeDADYo6DAqiOD7qDdfhTXtkDbxi3SxGC7x0CVoYD7=v8m' \
                 '=YDhxDCXGPDwOA8DieFqtvp2EhIiDh8D7vhDla4Efw8bf3LSmvI+b3GAiKDXEdDvaHw0OoDUn9z9x7N=ghelWGeoA' \
                 '+KiiGYdWmxdYhK+AqezL2NvW0D+m0DKDhrTWauDDaKWC+DD=; ' \
                 'ssxmod_itna2=Yq0x9Qi=D=3CqYKGHLonBYGOCwP2oqY5E=G9Q5nKDBqbuGD7P2eOcFYOD7mLYC2TIxF8e42xLPRDn+UdPk/QE' \
                 '=vRiRRwnz07OAE2ma8t7GN=OptQ=Tw76RaedBRbQVkMLA1UmEgy3D9aDcFasZIKu0nhecFNQ6eW/ZBsogmOFxxh' \
                 '+AubrQv3yCc4u12rMx2sHOgQZGBrRr5xi0RwNrWN9AxGH2BCK' \
                 '=GqLtvYR020tEwK9Yoed6dRXCTmFSlaQy7fHgSIc1Z1zdEOUpWNaFkBBtn09zcDMeeTuBCWH9Lbb1Urtg3ra=sb9yheTT' \
                 '+er95u4AG04It5IUPkGALU2DmueaysW50RhiiDiSxHFFi+wPouA7qgivsUvtSrK' \
                 '+yTAPICTdeKm7gwI5rGiaGGLbbAj5qamn7Yz33rn+TYvoD07X0D0uvHoaNMN0if2WdLiN9Of/nDrbeVO5wcPNO5KGOwaKtYx' \
                 '+DDLxD29hDD; ' \
                 'FCNEC=%5B%5B%22AKsRol_A272GwTpSrWnIixNbmuZeK' \
                 '-zOr2GstwUB3CCAFfGlMCBVKU9xd54pCDOMIX7qkq3eVq4G8fzsDs6uoLrxSQ01IHp4a1kyUpoEGDUAaTaJqeTGskHm6fl2Y6vSWiARPqUC2hkGnZRHMKonR3NKpaQevZCaZQ%3D%3D%22%5D%2Cnull%2C%5B%5D%5D; dc_session_id=10_1678450164699.709836; c_first_ref=www.google.com.hk; c_segment=9; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1678195438,1678202290,1678368613,1678450167; dc_sid=0a0e751d54dcf89b20e1c535323add63; c_dl_prid=1678202570565_603287; c_dl_rid=1678450178421_918223; c_dl_fref=https://blog.csdn.net/qq_33876553/article/details/79730246; c_dl_fpage=/download/weixin_38677806/12861319; c_dl_um=-; c_utm_medium=distribute.pc_relevant_t0.none-task-download-2%7Edefault%7ECTRLIST%7EAntiPaid-1-12861319-blog-79730246.pc_relevant_aa; c_utm_relevant_index=1; FPTOKEN=JglP6xJ3tLlgUIPfcDjBw9+Z8RcS9lboYSD0S0Dg8WE8KMjXAFWDT33F+xGWko24D9qPN9jT5amfJbet7knd374UMscAo6Mu5uhoGIBQ0Dn5pzyWmAngBgXa/XsNPvi7vX0Z/i3kzTls2KMUncRwrdCYmf15tpmB3hxrfC4X3eeQRSgt3+3z8thW43j6v3shNZreuP9nD3HDEmTV8xyGXQZdPZ1kNqT8dOUh6HBbny2Zlp45vHBuW/3R57o3goyJusk+tprePmh4pXJyljUiCAqaHXHxbTPqAbuS1rO8wZ220+ic4h8IrJSA0RHGIXv7Z87lV0Mve2dDS5pgi0/A1fxqsn3TETvSoxTZXL/YTRx6sZjmNFhkAnaLlz4xJF98KoCWcc8wAnJcuw0RjAnv1SXNe7RB283xDbi8atHcSg3eVS9V0f9aszPXZ5rgKkR7|HU0lmU2o5GEBzGgmDAznOOTkgkqZ+FlxfHjH/PI7q6k=|10|cc937f84a4176dc262e8d06e7df89d5e; c_first_page=https%3A//blog.csdn.net/qq_33876553/article/details/79730246; c_dsid=11_1678451213110.383161; c_page_id=default; c_pref=https%3A//www.google.com.hk/; c_ref=https%3A//blog.csdn.net/qq_33876553/article/details/79730246; dc_tos=rrb1le; log_Id_pv=148; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1678451666; log_Id_view=494; log_Id_click=200 '
        cd = {s.split("=")[0].strip(): s.split("=")[1].strip() for s in cookie.split(";")}
        self.session = requests.session()
        self.session.cookies.update(cookiejar_from_dict(cd))
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                   'Chrome/110.0.0.0 Safari/537.36 ',
                                     'origin': 'https://editor.csdn.net',
                                     'referer': 'https://editor.csdn.net/'})

        self.source = source
        self.output_dir = output_dir

    def upload_img(self, filepath: str):
        filepath = os.path.abspath(filepath)

        def build_multipart():
            ext = os.path.splitext(filepath)[1][1:]
            filename = os.path.basename(filepath)
            upoload_info = self._access(ext)
            upoload_info['OSSAccessKeyId'] = upoload_info['accessId']
            upoload_info['key'] = upoload_info['filePath']
            upoload_info['success_action_status'] = '200'
            upoload_info['callback'] = upoload_info['callbackUrl']
            upoload_info['file'] = (
                filename, open(filepath, 'rb'), f'image/{ext}')
            return MultipartEncoder(fields=upoload_info,
                                    boundary='----WebKitFormBoundarylnuHFe8ZGBIq3XTg')

        multipart = build_multipart()
        upload_url = multipart.fields['host']
        hostname = urlparse(upload_url).hostname
        logger.debug(f"uploading {filepath} to {hostname}")
        response = requests.post(upload_url, headers={'Content-Type': multipart.content_type,
                                                      'Origin': 'https://editor.csdn.net',
                                                      'Host': hostname,
                                                      'Referer': 'https://editor.csdn.net/',
                                                      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                                    'Chrome/110.0.0.0 Safari/537.36 '
                                                      },
                                 data=multipart)
        response.raise_for_status()
        img_url = response.json()['data']['imageUrl']
        logger.info(f"upload {filepath} success: {img_url}")
        return img_url

    def _access(self, img_ext: str):
        params = {
            'type': 'blog',
            'rtype': 'markdown',
            'x-image-template': 'standard',
            'x-image-app': 'direct_blog',
            'x-image-dir': 'direct',
            'x-image-suffix': img_ext,
        }
        response = self.session.get("https://imgservice.csdn.net/direct/v1.0/image/upload", params=params)
        response.raise_for_status()
        logger.trace(response.text)
        logger.trace(response.request.headers)
        upload_info = response.json()['data']
        logger.info("access filepath success: %s" % upload_info['filePath'])
        return upload_info

    def replace(self, blog_path, tar_path):
        logger.info(f"start handle {blog_path}")

        def sub_img(pat) -> str:
            img_desc, img_url = pat.group(1), pat.group(2)
            if urlparse(img_url).hostname is None:
                if img_url.startswith('/') or img_url.startswith('\\'):
                    img_url = img_url[1:]
                logger.trace(img_url)
                img_path = os.path.join(os.path.dirname(blog_path), unquote(img_url))
                csdn_url = self.upload_img(img_path)
                logger.debug(f"replace {img_url} to {csdn_url}")
                return f'![{img_desc}]({csdn_url})'
            else:
                return pat.group()

        def sub_link(pat) -> str:
            full_url = urljoin('http://windcf.com', pat.group(2))
            return f'[{pat.group(1)}]({full_url})'

        with open(blog_path, encoding='utf-8') as f:
            content = f.read()
            new_content = re.sub(r"!\[(.*)]\((.+)\)", sub_img, content)

        new_content = re.sub(r'[^!]\[(.*)]\((/archives/\d+)\)', sub_link, new_content)

        Path(tar_path).write_text(new_content, encoding='utf-8')

        logger.info(f"write {tar_path} successfully")

    def run(self):
        source = os.path.abspath(self.source)

        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        if os.path.isdir(source):
            for root, _, filenames in os.walk(source):
                for filename in filenames:
                    if not filename.endswith(".md"):
                        continue
                    abspath = os.path.join(root, filename)
                    tar_path = os.path.join(outdir, Path(abspath).relative_to(source))
                    if os.path.exists(tar_path):
                        continue
                    self.replace(abspath, tar_path)

        else:
            tar_path = os.path.join(self.output_dir, os.path.basename(source))
            self.replace(source, tar_path)


if __name__ == '__main__':
    # uploader.upload_img('./x86-64.png')
    # print(os.path.splitext('./x86-64.png')[1][1:])
    # source = r'C:\Users\chunf\Desktop\halo-backup-markdown-2023-03-09-21-33-28-875883832\-1833193175'
    outdir = "D:/output"
    uploader = CsdnBlogUploader(
        r'C:\Users\chunf\OneDrive\桌面\halo-backup-markdown',
        outdir)
    uploader.run()
    # for root, _, filenames in os.walk(source):
    #     for filename in filenames:
    #         if filename.endswith('.md'):
    #             abspath = os.path.join(root, filename)
    #             print(os.path.join(outdir, Path(abspath).relative_to(source)))
    # print(unquote('QQцИкхЫ╛20211103102056-3f7aa7c5f9de4ae299cb047df581c594'))
