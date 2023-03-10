import logging
import os.path
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from loguru import logger
from requests.utils import cookiejar_from_dict
from requests_toolbelt.multipart.encoder import MultipartEncoder

logger.remove()
logger.add(sys.stderr, level=logging.INFO,
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
                 '%22scope%22%3A1%7D%7D; c_dl_prid=1676464927313_161427; c_dl_rid=1678202570565_603287; ' \
                 'c_dl_fref=https://blog.csdn.net/l_mloveforever/article/details/112725753; ' \
                 'c_dl_fpage=/download/ice_yulong/7237657; ' \
                 'c_dl_um=distribute.pc_relevant.none-task-blog-2%7Edefault%7Ebaidujs_baidulandingword%7Edefault-0' \
                 '-112725753-blog-95481787.pc_relevant_landingrelevant; dc_session_id=10_1678368608168.480254; ' \
                 'c_first_ref=www.google.com.hk; c_first_page=https%3A//www.csdn.net/; ' \
                 'c_dsid=11_1678368611254.328036; c_segment=9; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1677766157,' \
                 '1678195438,1678202290,1678368613; dc_sid=7e32b15ce427e0bee1c28e6f50452847; ' \
                 '_gid=GA1.2.706525915.1678368614; ' \
                 'ssxmod_itna=eqAxyDuDcQitT4BPOe5DkQDCiHZ1YlY4iIxbdD/KW+DnqD=GFDK40EYO4=D73goEGvKqEe+0++tE/i7PEK=Q' \
                 '+iTfdtdWE4GLDmKDyiG4TeDxOq0rD74irDDxD3DbSdDSDWKD9D0' \
                 '+kSBuqtDm4GWlqDgS4GgKniD0StyiMiD4qDBGEdDKTryDGAUtlt=LqxNq2=DjTrD/bxFg2' \
                 '=dkZazSuTTqh0WiqGySPGuRdbSneDH+MNZYjevYhGYlhe=+ihai7D=8GDzSD8e8Gvxe5xGj78AWGeiif4sC5DAKX+2eD===; ' \
                 'ssxmod_itna2=eqAxyDuDcQitT4BPOe5DkQDCiHZ1YlY4iIxbG9i5i8iDBTrLx7Pb' \
                 '+8NjHD7Ax8he614qtn0LxDa4Eybk3bbuv44tVEmeom32tmyL+Qg4W7uUQXYcMgEni0k0cnusuqIbs5fsoTZxrgwr' \
                 '=o7FICpOmCP4qEFHIhWh=/+H/ebq3Fo=YZwxNcnN3lov8lE87ofpCzwkGUiLCbDxwbEjIbE4489E5iMNeYSX5rO5p' \
                 '=OicQYvqWSNQ48Yy+Pw4q=cu4ZPDEZt7pCEQTgoksCuCsScqMQg1NdFfbOrcD=izUwGCL2a7LIGNTFAKKcIv8myinHHty8Bys' \
                 '+e6Rw=iDQe+pWuut77KRmGBtBYOfAWKud7el7RK1qo' \
                 '+45aOLDq9IWf0A9DgQvnjG5P5IOIWtkTohpWDo5kGB8PI33afPiqAYVxytIA8S=a5oav7tFa1p2SFNcvISK5XD3D07H' \
                 '+Po2blAKu7YtBjrkDfpKjPxeGeD7=DYKNeD==; firstDie=1; ' \
                 'FPTOKEN=E5Re19Izm33AUfiGQbH41zgXc3LlhKvutRixYQKUPpxKIORhygGoVlRBMbjQ0JZ3TwCPrUFIS3GynFeXx+VxaxNcNv' \
                 '+BpnjDjY44dxe6tX9xvmxahXUJjnTOzdWouSTcvggjOKEZUaULO7FWE0zuWOqcipZq8/gDax1S18EyHwtEwB' \
                 '+QLNx09GbTmd1KqSreA+8N/1OuKyRELQQGS7DSHEVtP/2M1MopxlQF9W8u/7xwViDPzSGgZfzS9DscIV04BR9N/uPFeRND4z4hS' \
                 '+DUwGfmcHcdeXNn5tom9wpuIeR27qR6ZGX2mTPsfuFjDSieQDrvo0r35KuySEtbbkK/tLYia2QkoeB+x74Zb8Z+cDFev' \
                 '/RGel5ymOBwrm9kV+RSQttqPVY5D8em/GFzUBmRw8KbGzSYe/4zp4Z4SKAFR/+z5Ie4Cq+7var7HI8bpi5X' \
                 '|/ml79wEXLStpDeeo+c7wPh+2HHut4DL69WZ+FmNtvY0=|10|e18c4cebac4ab701139c42b0f420dd3d; ' \
                 'c_page_id=default; ' \
                 '__gpi=UID=00000bb6a7cdd736:T=1675681213:RT=1678369392:S=ALNI_MZK6Ket09W9llhZ7ATI_OwUuHLPFw; ' \
                 'FCNEC=%5B%5B%22AKsRol9ACa1Vxtbeu_SwbVHD7CtNauUkmiSaa4ivPpSNxEiPcmptRy2y3dBf3k7yXz' \
                 '-jQ9qmV7RD_rXx0bnULk9YoCGzRrz4PX7XVq-PTE3DiLWllcrf_mw1ygwVQFgdtVvjyR-3rIuM57Xj3HUMZu-HKQwQH6TmmA%3D' \
                 '%3D%22%5D%2Cnull%2C%5B%5D%5D; c_pref=https%3A//mp.csdn.net/mp_blog/creation/success/129432053; ' \
                 'c_ref=https%3A//blog.csdn.net/weixin_43701894/article/details/129432053%3Fcsdn_share_tail%3D%257B' \
                 '%2522type%2522%253A%2522blog%2522%252C%2522rType%2522%253A%2522article%2522%252C%2522rId%2522%253A' \
                 '%2522129432053%2522%252C%2522source%2522%253A%2522weixin_43701894%2522%257D; log_Id_pv=121; ' \
                 'dc_tos=rr9a6i; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1678369482; log_Id_view=432; ' \
                 'log_Id_click=118 '
        cd = {s.split("=")[0].strip(): s.split("=")[1].strip() for s in cookie.split(";")}
        self.session = requests.session()
        self.session.cookies.update(cookiejar_from_dict(cd))

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
        upload_info = response.json()['data']
        logger.info("access filepath success: %s" % upload_info['filePath'])
        return upload_info

    def replace_img_url(self, blog_path, tar_path):
        logger.info(f"start handle {blog_path}")

        def sub(pat) -> str:
            img_url = pat.group(1)
            if urlparse(img_url).hostname is None:
                if img_url.startswith('/') or img_url.startswith('\\'):
                    img_url = img_url[1:]
                img_path = os.path.join(os.path.dirname(blog_path), img_url)
                csdn_url = self.upload_img(img_path)
                logger.debug(f"replace {img_url} to {csdn_url}")
            else:
                return img_url

        with open(blog_path, encoding='utf-8') as f:
            content = f.read()
            new_content = re.sub(r"!\[.*]\((.+)\)", sub, content)

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
                    self.replace_img_url(abspath, tar_path)

        else:
            tar_path = os.path.join(self.output_dir, os.path.basename(source))
            self.replace_img_url(source, tar_path)


if __name__ == '__main__':
    # uploader.upload_img('./x86-64.png')
    # print(os.path.splitext('./x86-64.png')[1][1:])
    # source = r'C:\Users\chunf\Desktop\halo-backup-markdown-2023-03-09-21-33-28-875883832\-1833193175'
    outdir = "D:/output"
    uploader = CsdnBlogUploader(
        r'C:\Users\chunf\Desktop\halo-backup-markdown-2023-03-09-21-33-28-875883832\-1833193175\某网站加密参数分析-某网站加密参数分析.md',
        outdir)
    uploader.run()
    # for root, _, filenames in os.walk(source):
    #     for filename in filenames:
    #         if filename.endswith('.md'):
    #             abspath = os.path.join(root, filename)
    #             print(os.path.join(outdir, Path(abspath).relative_to(source)))
