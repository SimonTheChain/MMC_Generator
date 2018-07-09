#!/usr/bin/python3
# -*- coding: utf-8 -*-

# MMC Generator
#
# Author: Simon Lachaîne

"""
Workflow:
-User input: Select platform
-User input: Enter root dir
-Search for files
-Sort files
-Identify files
-Create presentations for files
-Create experiences for presentations
-Create ALID for experiences
-Create xml
"""

import os
import re
import logging

import lxml.etree as etree


class Asset(object):
    """
    Stores information about assets
    """
    LOCALES = {  # to complete
        "English": "en",
        "French": "fr",
    }

    def __init__(self):
        self.filename = ""
        self.locale = ""
        self.content_id = ""


class AudioVideo(object):

    PROGRAM_TYPES = [
        "feature",
        "trailer",
        "episode",
        "bonus",
    ]

    def __init__(self):
        self.asset = Asset()
        self.program_type = ""
        self.dub = False



class Text(object):
    """
    Stores information about text assets
    """
    TEXT_TYPE = {
        "Full": "normal",
        "Forced": "forced",
        "SDH": "SDH",
    }
    FRAMERATE = {  # to complete
        "23.98fps": {
            "multiplier": "1000/1001",
            "timecode": "NonDrop",
            "framerate": "24",
        },
        "24fps": "",
        "25fps": "",
        "30fps Drop": "",
        "30fps Non-Drop": "",
    }

    def __init__(self):
        self.asset = Asset()
        self._extension = ""
        self.text_type = ""
        self.framerate = ""

    @property
    def extension(self):
        return self._extension

    @extension.setter
    def extension(self, filename):
        self._extension = os.path.splitext(filename)[1]


class Poster(object):
    """
    Stores information about poster art assets
    """

    def __init__(self):
        self.asset = Asset()
        self.width = ""
        self.height = ""
        self._encoding = ""

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, filename):
        self._encoding = os.path.splitext(filename)[1]


class MetaGeneric(object):
    """
    Stores generic metadata information
    """
    PROVIDERS = {  # to complete
        "eOne": "e1",
        "Under the Milky Way": "utmw",
    }

    def __init__(self):
        self.provider_id = ""


class MetaFeature(object):
    """
    Stores feature metadata information
    """
    def __init__(self):
        self.meta_generic = MetaGeneric()
        self.feature_id = ""
        self.movie_xml = Asset()
        self.trailer_xml = []  # list of Asset instances


class MetaEpisodic(object):
    """
    Stores episodic metadata information
    """
    def __init__(self):
        self.meta_generic = MetaGeneric()
        self.season_id = ""
        self.episode_id = ""
        self.series_xml = Asset()
        self.season_xml = Asset()
        self.episode_xml = Asset()


class FileFinder(object):
    """
    Searches for files and sorts them
    """
    def __init__(self, root_path):
        self.root_path = root_path
        self.files_found = []
        self.mov = []
        self.itt = []
        self.scc = []
        self.jpg = []
        self.xml = []
        self.unrecognized = []

    def find_files(self):
        """
        Searches for files in a given directory
        :return: list of files
        """
        if not os.path.isdir(self.root_path):
            raise ValueError("The root directory is invalid")

        for root, dirs, files in os.walk(self.root_path):

            for f in files:
                self.files_found.append(f)

        return self.files_found

    def sort_files(self):
        """
        Identifies file types from a list
        :return: lists of instances according to file type
        """
        if not self.files_found:
            raise ValueError("No files to identify")

        for f in self.files_found:
            if os.path.splitext(f)[1] == ".mov":
                mov = Asset()
                mov.filename = os.path.basename(f)
                self.mov.append(mov)

            elif os.path.splitext(f)[1] == ".itt":
                sub = Text()
                sub.asset.filename = os.path.basename(f)
                self.itt.append(sub)

            elif os.path.splitext(f)[1] == ".scc":
                scc = Text()
                scc.asset.filename = os.path.basename(f)
                self.scc.append(scc)

            elif os.path.splitext(f)[1] == ".jpg":
                poster = Poster()
                poster.asset.filename = os.path.basename(f)
                self.jpg.append(poster)

            elif os.path.splitext(f)[1] == ".xml":
                xml = Asset()
                xml.filename = os.path.basename(f)
                self.xml.append(xml)

            else:
                self.unrecognized.append(os.path.basename(f))

        return self.mov, self.itt, self.scc, self.jpg, self.xml, self.unrecognized

    def identify_amazon(self):
        pass

    def identify_google(self):
        pass


class IdentifyMicrosoft(object):
    """docstring for IdentifyMicrosoft"""

    def __init__(self):
        self.assets = []
        self.pattern_general = re.compile("^([^_]+)_[^_]+_([^_]+)_.+")
        self.pattern_locale = re.compile("(?:.+_){3,4}([a-z][a-z])(-[A-Z][A-Z])?(-419)?")
        
    @staticmethod
    def _cut_locale(match):
        if not match.group(2) and not match.group(3):
            return match.group(1)

        elif match.group(3):
            return match.group(1) + match.group(3)

        elif match.group(1) == "es" or match.group(1) == "pt":
            return match.group(1) + match.group(2)

        else:
            return match.group(1)

    def find_framerate(self, itt):
        """
        Parse itt files to find the framerate
        :return:
        """
        parser = etree.XMLParser(remove_blank_text=True, encoding="utf-8")
        nsmap = {
            "ttp": "http://www.w3.org/ns/ttml#parameter"
        }

        with open(os.path.join(self.root_path + os.sep, itt), "r", encoding="utf-8") as itt_file:
            try:
                sub = etree.parse(itt_file, parser=parser)

            except etree.XMLSyntaxError as e:
                raise etree.XMLSyntaxError(e)

            else:
                sub_root = sub.getroot()
                attributes = sub_root.attrib
                framerate = attributes["{%s}frameRate" % nsmap["ttp"]]
                multiplier = attributes["{%s}frameRateMultiplier" % nsmap["ttp"]]
                drop = attributes["{%s}dropMode" % nsmap["ttp"]]

                return framerate, multiplier, drop

    def read_assets(self, mov, itt, scc, jpg, xml, unrecognized):
        """
        Identifies assets and creates objects accordingly
        :return:
        """
        for m in mov:
            if "AudioOnly" in m:
                if "Feature" in m:
                    f = Asset()
                    f.filename = m
                    match_locale = self.pattern_locale.search(m)
                    f.locale = self._cut_locale(match_locale)

                    self.feature_dubs[m] = self._cut_locale(match_locale)

                elif "Trailer" in m:
                    match_locale = self.pattern_locale.search(m)
                    self.trailer_dubs[m] = self._cut_locale(match_locale)

            elif "Feature" in m:
                match_general = self.pattern_general.search(m)
                self.provider = match_general.group(1)
                self.vendor_id = match_general.group(2)
                match_locale = self.pattern_locale.search(m)
                self.feature[m] = self._cut_locale(match_locale)

            elif "Trailer" in m:
                match_locale = self.pattern_locale.search(m)
                self.trailer[m] = self._cut_locale(match_locale)

            else:
                pass  # to complete

        for s in self.scc:
            if "Feature" in s:
                match_locale = self.pattern_locale.search(s)
                self.feature_captions[s] = self._cut_locale(match_locale)

            elif "Trailer" in s:
                match_locale = self.pattern_locale.search(s)
                self.trailer_captions[s] = self._cut_locale(match_locale)

            else:
                pass  # to complete

        for i in self.itt:
            if "Feature" in i and "Full" in i:
                match_locale = self.pattern_locale.search(i)
                locale = self._cut_locale(match_locale)
                self.feature_full_subs[i] = locale

            elif "Feature" in i and "Forced" in i:
                match_locale = self.pattern_locale.search(i)
                locale = self._cut_locale(match_locale)
                self.feature_forced_subs[i] = locale

            elif "Trailer" in i and "Full" in i:
                match_locale = self.pattern_locale.search(i)
                locale = self._cut_locale(match_locale)
                self.trailer_full_subs[i] = locale

            elif "Trailer" in i and "Forced" in i:
                match_locale = self.pattern_locale.search(i)
                locale = self._cut_locale(match_locale)
                self.trailer_forced_subs[i] = locale

            else:
                pass  # to complete

        for j in self.jpg:
            match_locale = self.pattern_locale.search(j)
            self.poster[j] = self._cut_locale(match_locale)

        return self.provider, \
               self.vendor_id, \
               self.feature, \
               self.trailer, \
               self.feature_full_subs, \
               self.feature_forced_subs, \
               self.trailer_full_subs, \
               self.trailer_forced_subs, \
               self.poster


class Presentation(object):
    ASSET_TYPES = {
        "video": "vidtrackid",
        "audio": "audtrackid",
        "subs": "subtrackid",
        "captions": "subtrackid",
        "poster": "",
        "metadata": "",
    }
    VIDEO_TYPES = [
        "feature",
        "trailer",
    ]
    def __init__(self, provider, vendor_id, asset_type, asset, locale):
        self.provider = provider
        self.vendor_id = vendor_id
        self.asset_type = asset_type
        self.asset = asset
        self.locale = locale
        self.presentation = ""

    def create_presentation(self):
        presentation = "md:{track}:org:{provider}:{vendor_id}:{video_type}.{asset}.{locale}".format(
            track=self.ASSET_TYPES[self.asset_type],
            provider=self.provider,
            vendor_id=self.vendor_id,
            video_type="feature",  # to change
            asset=self.asset,
            locale=self.locale,
        )
        self.presentation = presentation
        return self.presentation


class Experience(object):
    COUNTRIES = [
        "CA",
        "US",
        "GB",
        "IE",
        "IT",
    ]


class CreateMmc(object):
    """
    Creates the MMC xml
    """
    def __init__(self):
        self.meta_feature = MetaFeature()
        self.meta_episodic = MetaEpisodic()
        self.file_finder = FileFinder()
        self.running = False
        self.output_path = ""
        self.tracks = []
        self.presentations = []
        self.experiences = []

    @staticmethod
    def _root():
        nsmap = {
            "manifest": "http://www.movielabs.com/schema/manifest/v1.5/manifest",
            "md": "http://www.movielabs.com/schema/md/v2.4/md",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }
        schemalocation = "http://www.movielabs.com/schema/manifest/v1.5/manifest manifest-v1.5.xsd"

        root = etree.Element(
            "{%s}MediaManifest" % nsmap["manifest"],
            attrib={"{" + nsmap["xsi"] + "}schemaLocation": schemalocation},
            nsmap=nsmap)

        return nsmap, root

    @staticmethod
    def _spec_version(nsmap, root):
        xml_compatibility = etree.SubElement(root, "{%s}Compatibility" % nsmap["manifest"])
        xml_specversion = etree.SubElement(xml_compatibility, "{%s}SpecVersion" % nsmap["manifest"])
        xml_specversion.text = "1.5"
        xml_profile = etree.SubElement(xml_compatibility, "{%s}Profile" % nsmap["manifest"])
        xml_profile.text = "MMC-1"

    @staticmethod
    def _inventory(nsmap, root):
        inventory = etree.SubElement(root, "{%s}Inventory" % nsmap["manifest"])

        return inventory


class MmcController(object):
    PLATFORMS = [
        "Amazon",
        "Google",
        "Microsoft",
    ]

    def __init__(self):
        self._platform = ""
        self.root_path = ""

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, pf):
        if pf not in self.PLATFORMS:
            raise ValueError("Invalid platform")

        self._platform = pf

    def search_directory(self):
        file_finder = FileFinder(root_path=self.root_path)
        file_finder.find_files()
        file_finder.sort_files()

    def identify_files(self):
        if self.platform == "Microsoft":
            ms = IdentifyMicrosoft()


def main():
    mmc_obj = CreateMmc()
    mmc_obj.meta_feature.meta_generic.provider = "E1"
    mmc_obj.meta_feature.feature_id = "FEATUREID"



