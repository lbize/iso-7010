#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2025 Laurent BIZE
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import os
import re
import pathlib
from bs4 import BeautifulSoup

def extract_iso_7010_data():
    agent = "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
    headers =  {
        "User-Agent": agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }
    url = "https://en.wikipedia.org/wiki/ISO_7010"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract all table data (if any)
    spans = soup.find_all('span', {'typeof':'mw:File'})
    pathlib.Path("assets").mkdir(parents=True, exist_ok=True)
    with open("lib.typ", "w") as lib, open("manual.typ", "w") as libm:
        libm.write(f"""
#import "@preview/tidy:0.4.3": *
#import "lib.typ"

= Introduction

This Typst library provides SVG for all the ISO 7010 safety signs, minus country-specific variants and outdated signs.

Thanks to *Wikipedia*, *Wikimedia Commons* and all the *authors* of these SVG drawing for providing the #link("https://fr.wikipedia.org/wiki/ISO_7010")[ISO 7010] icons under a free licence.

= Documentation

This section provides an overview for the available icons. You shall import first the image you want to use. To avoid memory issues, you may import only the icons you need.

#let module = parse-module(
  read("lib.typ"),
  name: "ISO7010",
  scope: (
""")
        entries = dict()
        for i, s in enumerate(spans, start=0):
            a = s.select_one('a:first-child')
            if a is not None and 'href' in a.attrs and 'title' in a.attrs:
                href= a['href']
                title= a['title']
                tvat = re.sub(r'^(ISO_7010_[EFMWP][0-9]{3}).*\.svg$',r'\g<1>',re.sub(r'^File:','',os.path.basename(href)))
                if tvat not in entries and not tvat.startswith("NEN") and re.match(r'ISO_7010_[EFMWP][0-9]{3}',tvat):
                    entries[tvat] = None
                    libm.write(f"    {tvat}: lib.{tvat},\n")
                    lib.write(f"/// SVG raw image {tvat}: {title}\n")
                    lib.write(f"///\n")
                    lib.write(f"/// #example(`#image({tvat}, format:\"svg\",width:6em)`)\n")
                    lib.write(f"///\n")
                    lib.write(f"/// Source (including licencing): http://commons.wikimedia.org{href}\n")
                    lib.write(f"///\n")
                    lib.write(f"/// -> content\n")
                    lib.write(f"#let {tvat} = read(\"assets/{tvat}.svg\",encoding: none)\n")
                    #response_img = requests.get(f"https://en.wikipedia.org{href}", headers=headers)
                    #if response_img.status_code == 200:
                    #  img_soup = BeautifulSoup(response_img.content, 'html.parser')
                    #  div = img_soup.find('div', class_='fullImageLink')
                    #  ai = div.select_one('a:first-child')
                    #  if ai is not None and 'href' in ai.attrs:
                    #    href_img = ai['href']
                    #    with open(f"assets/{tvat}.svg", "wb") as f:
                    #      f.write(requests.get(f"https:{href_img}", headers=headers).content)
        libm.write(f"""  
  ),)
#show-module(
  module,
  show-outline: false,
  style: styles.minimal,
)
""")
if __name__ == "__main__":
    extract_iso_7010_data()
