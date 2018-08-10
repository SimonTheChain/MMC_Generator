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
    ASSET_TYPES = {
        "video": "vidtrackid",
        "audio": "audtrackid",
        "subs": "subtrackid",
        "captions": "subtrackid",
        "poster": "",
        "metadata": "",
    }
    LOCALES = {  # to complete
        "English": "en",
        "French": "fr",
    }
    PROGRAM_TYPES = [
        "feature",
        "trailer",
        "episode",
        "bonus",
    ]
    TEXT_TYPES = {
        "Full": "normal",
        "Forced": "forced",
        "SDH": "SDH",
    }
    FRAMERATES = {  # to complete
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
        self.filename = ""
        self.asset_type = ""
        self.locale = ""
        self.provider = ""
        self.vendor_id = ""
        self.track_id = ""
        self.program_type = ""

        # video assets
        self.dub = False

        # text assets
        self.text_type = ""
        self.framerate = ""

        # poster art
        self.width = ""
        self.height = ""

    def create_presentation(self):
        presentation = "md:{track}:org:{provider}:{vendor_id}:{video_type}.{asset}.{locale}".format(
            track=self.ASSET_TYPES[self.asset_type],
            provider=self.provider,
            vendor_id=self.vendor_id,
            video_type=self.program_type,
            asset=self.asset_type,
            locale=self.locale,
        )
        self.track_id = presentation
        return self.track_id


class FileFinder(object):
    """
    Searches for files and sorts them
    """
    def __init__(self):
        self.files_found = []
        self.mov = []
        self.itt = []
        self.scc = []
        self.jpg = []
        self.xml = []
        self.unrecognized = []
        self.identify_ms = IdentifyMicrosoft()

    def find_files(self, path):
        """
        Searches for files in a given directory
        :return: list of files
        """
        if not os.path.isdir(path):
            raise ValueError("The root directory is invalid")

        for root, dirs, files in os.walk(path):

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
                sub = Asset()
                sub.filename = os.path.basename(f)
                self.itt.append(sub)

            elif os.path.splitext(f)[1] == ".scc":
                scc = Asset()
                scc.filename = os.path.basename(f)
                self.scc.append(scc)

            elif os.path.splitext(f)[1] == ".jpg":
                poster = Asset()
                poster.filename = os.path.basename(f)
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

    def read_mov(self, mov):
        """
        Identifies *.mov assets and creates objects accordingly
        :return:
        """
        if isinstance(mov, Asset):
            match_general = self.pattern_general.search(mov.filename)
            mov.provider = match_general.group(1)
            mov.vendor_id = match_general.group(2)
            match_locale = self.pattern_locale.search(mov.filename)
            mov.locale = self._cut_locale(match_locale)

            if "AudioOnly" in mov:
                if "Feature" in mov:
                    mov.program_type = "feature"
                    mov.dub = True

                elif "Trailer" in mov:
                    mov.program_type = "trailer"
                    mov.dub = True

            elif "Feature" in mov:
                mov.program_type = "feature"
                mov.dub = False

            elif "Trailer" in mov:
                mov.program_type = "trailer"
                mov.dub = False

            else:
                pass  # to complete

            return mov

    def read_scc(self, scc):
        if "Feature" in scc:
            match_locale = self.pattern_locale.search(scc)
            self.feature_captions[s] = self._cut_locale(match_locale)

        elif "Trailer" in scc:
            match_locale = self.pattern_locale.search(scc)
            self.trailer_captions[s] = self._cut_locale(match_locale)

        else:
            pass  # to complete

    def read_itt(self):
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
        self.running = False
        self.output_path = ""
        self.feature_id = ""
        self.series_id = ""
        self.season_id = ""
        self.episode_id = ""

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

    def _feature_audio(self, nsmap, inventory, mov):
        audio_comment = etree.Comment("Main audio file for the feature")
        inventory.append(audio_comment)
        self.presentation_audio_main = "md:audtrackid:org:{provider}:{vendor_id}:feature.audio.{locale}".format(
            provider=mov.provider,
            vendor_id=mov.vendor_id,
            locale=mov.locale
        )
        xml_audio_main = etree.SubElement(
            inventory,
            "{%s}Audio" % nsmap["manifest"],
            attrib={"AudioTrackID": self.presentation_audio_main})
        xml_audio_type_main = etree.SubElement(xml_audio_main, "{%s}Type" % nsmap["md"])
        xml_audio_type_main.text = "primary"
        xml_audio_locale_main = etree.SubElement(xml_audio_main, "{%s}Language" % nsmap["md"])
        xml_audio_locale_main.text = mov.locale
        xml_audio_container_ref = etree.SubElement(xml_audio_main, "{%s}ContainerReference" % nsmap1["manifest"])
        xml_audio_container_loc = etree.SubElement(
            xml_audio_container_ref,
            "{%s}ContainerLocation" % nsmap["manifest"])
        xml_audio_container_loc.text = "file://resources/%s" % mov.filename


class MmcController(object):
    PLATFORMS = [
        "Amazon",
        "Google",
        "Microsoft",
    ]

    def __init__(self):
        self._platform = ""
        self._root_path = ""
        self.output_path = ""
        self.file_finder = FileFinder()
        self.mmc = CreateMmc()

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, pf):
        if pf not in self.PLATFORMS:
            raise ValueError("Invalid platform")

        self._platform = pf

    @property
    def root_path(self):
        return self._root_path

    @root_path.setter
    def root_path(self, path):
        if not os.path.isdir(path):
            raise ValueError("Invalid package directory")

        self._root_path = path

    def search_directory(self):
        self.file_finder.find_files(self.root_path)
        self.file_finder.sort_files()

    def identify_files(self):
        if self.platform == "Microsoft":
            ms = IdentifyMicrosoft()
            [
                ms.read_mov(mov)
                for mov in self.file_finder.mov
            ]

    def create_presentations(self):
        for mov in self.file_finder.mov:
            mov.track_id = mov.create_presentation()

        for itt in self.file_finder.itt:
            itt.track_id = itt.create_presentation()

        for scc in self.file_finder.scc:
            scc.track_id = scc.create_presentation()

    def create_xml(self):
        for mov in self.file_finder.mov:
            if mov.asset_type == "video" and mov.program_type == "feature":
                self.mmc.test(mov)


def main():
    pass
