#!/usr/bin/python3
# -*- coding: utf-8 -*-

# MMC Generator
#
# Author: Simon Lachaîne


import os
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


class Text(object):
    """
    Stores information about text assets
    """
    TEXT_TYPE = {  # captions?
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
        self.trailer_xml = Asset()


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

    def __init__(self):
        self.root_path = ""
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

    @staticmethod
    def _audio_main(nsmap, inventory):
        audio_comment = etree.Comment("Main audio file")
        inventory.append(audio_comment)
        variables.mmc_ep_presentation_audio_main = "md:audtrackid:org:{0}:{1}:feature.audio.{2}".format(
            variables.mmc_ep_provider,
            variables.mmc_ep_id,
            variables.mmc_ep_video_locale)
        xml_audio_main = etree.SubElement(
            inventory,
            "{%s}Audio" % nsmap1["manifest"],
            attrib={"AudioTrackID": variables.mmc_ep_presentation_audio_main})
        xml_audio_type_main = etree.SubElement(xml_audio_main, "{%s}Type" % nsmap["md"])
        xml_audio_type_main.text = "primary"
        xml_audio_locale_main = etree.SubElement(xml_audio_main, "{%s}Language" % nsmap["md"])
        xml_audio_locale_main.text = variables.mmc_ep_video_locale
        xml_audio_container_ref = etree.SubElement(xml_audio_main, "{%s}ContainerReference" % nsmap1["manifest"])
        xml_audio_container_loc = etree.SubElement(
            xml_audio_container_ref,
            "{%s}ContainerLocation" % nsmap["manifest"])
        xml_audio_container_loc.text = "file://%s" % variables.mmc_ep_video_file

    def episodic(self):
        nsmap1 = {
            "manifest": "http://www.movielabs.com/schema/manifest/v1.5/manifest",
            "md": "http://www.movielabs.com/schema/md/v2.4/md",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }
        schemalocation = "http://www.movielabs.com/schema/manifest/v1.5/manifest manifest-v1.5.xsd"

        xml_root = etree.Element(
            "{%s}MediaManifest" % nsmap1["manifest"],
            attrib={"{" + nsmap1["xsi"] + "}schemaLocation": schemalocation},
            nsmap=nsmap1)

        xml_compatibility = etree.SubElement(xml_root, "{%s}Compatibility" % nsmap1["manifest"])
        xml_specversion = etree.SubElement(xml_compatibility, "{%s}SpecVersion" % nsmap1["manifest"])
        xml_specversion.text = "1.5"
        xml_profile = etree.SubElement(xml_compatibility, "{%s}Profile" % nsmap1["manifest"])
        xml_profile.text = "MMC-1"

        xml_inventory = etree.SubElement(xml_root, "{%s}Inventory" % nsmap1["manifest"])

        # audio
        audio_comment = etree.Comment("Main audio file")
        xml_inventory.append(audio_comment)
        variables.mmc_ep_presentation_audio_main = "md:audtrackid:org:{0}:{1}:feature.audio.{2}".format(
            variables.mmc_ep_provider,
            variables.mmc_ep_id,
            variables.mmc_ep_video_locale)
        xml_audio_main = etree.SubElement(
            xml_inventory,
            "{%s}Audio" % nsmap1["manifest"],
            attrib={"AudioTrackID": variables.mmc_ep_presentation_audio_main})
        xml_audio_type_main = etree.SubElement(xml_audio_main, "{%s}Type" % nsmap1["md"])
        xml_audio_type_main.text = "primary"
        xml_audio_locale_main = etree.SubElement(xml_audio_main, "{%s}Language" % nsmap1["md"])
        xml_audio_locale_main.text = variables.mmc_ep_video_locale
        xml_audio_container_ref = etree.SubElement(xml_audio_main, "{%s}ContainerReference" % nsmap1["manifest"])
        xml_audio_container_loc = etree.SubElement(
            xml_audio_container_ref,
            "{%s}ContainerLocation" % nsmap1["manifest"])
        xml_audio_container_loc.text = "file://%s" % variables.mmc_ep_video_file

        # audio dubs
        variables.mmc_ep_presentation_audios = []

        def create_audio_dubs(audio_dub_locale, audio_dub_file):
            audio_dub_comment = etree.Comment("Audio dub file")
            xml_inventory.append(audio_dub_comment)
            variables.mmc_ep_presentation_audios.append(
                "md:audtrackid:org:{0}:{1}:feature.audio.{2}".format(
                    variables.mmc_ep_provider,
                    variables.mmc_ep_id,
                    audio_dub_locale))
            xml_audio_dub = etree.SubElement(
                xml_inventory,
                "{%s}Audio" % nsmap1["manifest"],
                attrib={"AudioTrackID": "md:audtrackid:org:{0}:{1}:feature.audio.{2}".format(
                    variables.mmc_ep_provider,
                    variables.mmc_ep_id,
                    audio_dub_locale)})
            xml_audio_type_dub = etree.SubElement(xml_audio_dub, "{%s}Type" % nsmap1["md"])
            xml_audio_type_dub.text = "primary"
            xml_audio_locale_dub = etree.SubElement(
                xml_audio_dub,
                "{%s}Language" % nsmap1["md"],
                attrib={"dubbed": "true"})
            xml_audio_locale_dub.text = audio_dub_locale
            xml_audio_container_ref_dub = etree.SubElement(
                xml_audio_dub,
                "{%s}ContainerReference" % nsmap1["manifest"])
            xml_audio_container_loc_dub = etree.SubElement(
                xml_audio_container_ref_dub,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_audio_container_loc_dub.text = "file://%s" % audio_dub_file

        mmc_ep_audio_files = OrderedDict()
        if variables.mmc_ep_audio_file_1:
            mmc_ep_audio_files.update({variables.mmc_ep_audio_file_1: variables.mmc_ep_audio_locale_1})
        if variables.mmc_ep_audio_file_2:
            mmc_ep_audio_files.update({variables.mmc_ep_audio_file_2: variables.mmc_ep_audio_locale_2})
        if variables.mmc_ep_audio_file_3:
            mmc_ep_audio_files.update({variables.mmc_ep_audio_file_3: variables.mmc_ep_audio_locale_3})
        if variables.mmc_ep_audio_file_4:
            mmc_ep_audio_files.update({variables.mmc_ep_audio_file_4: variables.mmc_ep_audio_locale_4})
        if variables.mmc_ep_audio_file_5:
            mmc_ep_audio_files.update({variables.mmc_ep_audio_file_5: variables.mmc_ep_audio_locale_5})
        if variables.mmc_ep_audio_file_6:
            mmc_ep_audio_files.update({variables.mmc_ep_audio_file_6: variables.mmc_ep_audio_locale_6})
        if variables.mmc_ep_audio_file_7:
            mmc_ep_audio_files.update({variables.mmc_ep_audio_file_7: variables.mmc_ep_audio_locale_7})
        if variables.mmc_ep_audio_file_8:
            mmc_ep_audio_files.update({variables.mmc_ep_audio_file_8: variables.mmc_ep_audio_locale_8})
        if variables.mmc_ep_audio_file_9:
            mmc_ep_audio_files.update({variables.mmc_ep_audio_file_9: variables.mmc_ep_audio_locale_9})
        if variables.mmc_ep_audio_file_10:
            mmc_ep_audio_files.update({variables.mmc_ep_audio_file_10: variables.mmc_ep_audio_locale_10})

        for fichier in mmc_ep_audio_files.keys():
            create_audio_dubs(mmc_ep_audio_files[fichier], fichier)

        # video
        video_comment = etree.Comment("Main video file")
        xml_inventory.append(video_comment)
        variables.mmc_ep_presentation_feature = "md:vidtrackid:org:{0}:{1}:feature.video.{2}".format(
            variables.mmc_ep_provider,
            variables.mmc_ep_id,
            variables.mmc_ep_video_locale)
        xml_video = etree.SubElement(
            xml_inventory,
            "{%s}Video" % nsmap1["manifest"],
            attrib={"VideoTrackID": variables.mmc_ep_presentation_feature})
        xml_video_type = etree.SubElement(xml_video, "{%s}Type" % nsmap1["md"])
        xml_video_type.text = "primary"
        xml_video_picture = etree.SubElement(xml_video, "{%s}Picture" % nsmap1["md"])
        xml_video_container_ref = etree.SubElement(xml_video, "{%s}ContainerReference" % nsmap1["manifest"])
        xml_video_container_loc = etree.SubElement(
            xml_video_container_ref,
            "{%s}ContainerLocation" % nsmap1["manifest"])
        xml_video_container_loc.text = "file://%s" % variables.mmc_ep_video_file

        # captions
        if variables.mmc_ep_captions_file:
            captions_comment = etree.Comment("Captions file")
            xml_inventory.append(captions_comment)
            variables.mmc_ep_presentation_captions = "md:subtrackid:org:{0}:{1}:feature.captions.{2}".format(
                variables.mmc_ep_provider,
                variables.mmc_ep_id,
                variables.mmc_ep_captions_locale)
            xml_captions = etree.SubElement(
                xml_inventory,
                "{%s}Subtitle" % nsmap1["manifest"],
                attrib={"SubtitleTrackID": variables.mmc_ep_presentation_captions})
            xml_captions_type = etree.SubElement(xml_captions, "{%s}Type" % nsmap1["md"])
            xml_captions_type.text = "SDH"
            xml_captions_locale = etree.SubElement(xml_captions, "{%s}Language" % nsmap1["md"])
            xml_captions_locale.text = variables.mmc_ep_captions_locale

            xml_captions_speed = etree.SubElement(xml_captions, "{%s}Encoding" % nsmap1["md"])

            if variables.framerates[variables.mmc_ep_subs_speed][0] != "":
                xml_captions_framerate = etree.SubElement(
                    xml_captions_speed,
                    "{%s}FrameRate" % nsmap1["md"],
                    attrib={"multiplier": variables.framerates[variables.mmc_ep_subs_speed][0],
                            "timecode": variables.framerates[variables.mmc_ep_subs_speed][1]})
                xml_captions_framerate.text = variables.framerates[variables.mmc_ep_subs_speed][2]

            else:
                xml_captions_framerate = etree.SubElement(
                    xml_captions_speed,
                    "{%s}FrameRate" % nsmap1["md"])
                xml_captions_framerate.text = variables.framerates[variables.mmc_ep_subs_speed][2]

            xml_captions_container_ref = etree.SubElement(xml_captions, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_captions_container_loc = etree.SubElement(
                xml_captions_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_captions_container_loc.text = "file://%s" % variables.mmc_ep_captions_file

        # subtitles
        variables.mmc_ep_presentation_subs = []

        def create_subs(locale, sub_file, sub_type, sub_locale, speed):
            subs_comment = etree.Comment("Subtitle file")
            xml_inventory.append(subs_comment)

            if sub_type == "normal":
                variables.mmc_ep_presentation_subs.append("md:subtrackid:org:{0}:{1}:feature.subs.{2}".format(
                    variables.mmc_ep_provider,
                    variables.mmc_ep_id,
                    locale))
                xml_subs = etree.SubElement(
                    xml_inventory,
                    "{%s}Subtitle" % nsmap1["manifest"],
                    attrib={"SubtitleTrackID": "md:subtrackid:org:{0}:{1}:feature.subs.{2}".format(
                        variables.mmc_ep_provider,
                        variables.mmc_ep_id,
                        locale)})

            elif sub_type == "forced":
                variables.mmc_ep_presentation_subs.append("md:subtrackid:org:{0}:{1}:feature.forced.{2}".format(
                    variables.mmc_ep_provider,
                    variables.mmc_ep_id,
                    locale))
                xml_subs = etree.SubElement(
                    xml_inventory,
                    "{%s}Subtitle" % nsmap1["manifest"],
                    attrib={"SubtitleTrackID": "md:subtrackid:org:{0}:{1}:feature.forced.{2}".format(
                        variables.mmc_ep_provider,
                        variables.mmc_ep_id,
                        locale)})

            elif sub_type == "SDH":
                variables.mmc_ep_presentation_subs.append("md:subtrackid:org:{0}:{1}:feature.captions.{2}".format(
                    variables.mmc_ep_provider,
                    variables.mmc_ep_id,
                    locale))
                xml_subs = etree.SubElement(
                    xml_inventory,
                    "{%s}Subtitle" % nsmap1["manifest"],
                    attrib={"SubtitleTrackID": "md:subtrackid:org:{0}:{1}:feature.captions.{2}".format(
                        variables.mmc_ep_provider,
                        variables.mmc_ep_id,
                        locale)})

            xml_subs_format = etree.SubElement(xml_subs, "{%s}Format" % nsmap1["md"])
            xml_subs_format.text = os.path.splitext(sub_file)[1].replace(".", "").upper()
            xml_subs_type = etree.SubElement(xml_subs, "{%s}Type" % nsmap1["md"])
            xml_subs_type.text = sub_type
            xml_subs_locale = etree.SubElement(xml_subs, "{%s}Language" % nsmap1["md"])
            xml_subs_locale.text = sub_locale
            xml_subs_speed = etree.SubElement(xml_subs, "{%s}Encoding" % nsmap1["md"])

            if variables.framerates[speed][0] != "":
                xml_subs_framerate = etree.SubElement(
                    xml_subs_speed,
                    "{%s}FrameRate" % nsmap1["md"],
                    attrib={"multiplier": variables.framerates[speed][0],
                            "timecode": variables.framerates[speed][1]})
                xml_subs_framerate.text = variables.framerates[speed][2]

            else:
                xml_subs_framerate = etree.SubElement(
                    xml_subs_speed,
                    "{%s}FrameRate" % nsmap1["md"])
                xml_subs_framerate.text = variables.framerates[speed][2]

            xml_subs_container_ref = etree.SubElement(
                xml_subs, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_subs_container_loc = etree.SubElement(
                xml_subs_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_subs_container_loc.text = "file://%s" % sub_file

        if variables.mmc_ep_subs_file_1:
            create_subs(
                variables.mmc_ep_subs_locale_1,
                variables.mmc_ep_subs_file_1,
                variables.mmc_ep_subs_type_1,
                variables.mmc_ep_subs_locale_1,
                variables.mmc_ep_subs_speed)

        if variables.mmc_ep_subs_file_2:
            create_subs(
                variables.mmc_ep_subs_locale_2,
                variables.mmc_ep_subs_file_2,
                variables.mmc_ep_subs_type_2,
                variables.mmc_ep_subs_locale_2,
                variables.mmc_ep_subs_speed)

        if variables.mmc_ep_subs_file_3:
            create_subs(
                variables.mmc_ep_subs_locale_3,
                variables.mmc_ep_subs_file_3,
                variables.mmc_ep_subs_type_3,
                variables.mmc_ep_subs_locale_3,
                variables.mmc_ep_subs_speed)

        if variables.mmc_ep_subs_file_4:
            create_subs(
                variables.mmc_ep_subs_locale_4,
                variables.mmc_ep_subs_file_4,
                variables.mmc_ep_subs_type_4,
                variables.mmc_ep_subs_locale_4,
                variables.mmc_ep_subs_speed)

        if variables.mmc_ep_subs_file_5:
            create_subs(
                variables.mmc_ep_subs_locale_5,
                variables.mmc_ep_subs_file_5,
                variables.mmc_ep_subs_type_5,
                variables.mmc_ep_subs_locale_5,
                variables.mmc_ep_subs_speed)

        if variables.mmc_ep_subs_file_6:
            create_subs(
                variables.mmc_ep_subs_locale_6,
                variables.mmc_ep_subs_file_6,
                variables.mmc_ep_subs_type_6,
                variables.mmc_ep_subs_locale_6,
                variables.mmc_ep_subs_speed)

        if variables.mmc_ep_subs_file_7:
            create_subs(
                variables.mmc_ep_subs_locale_7,
                variables.mmc_ep_subs_file_7,
                variables.mmc_ep_subs_type_7,
                variables.mmc_ep_subs_locale_7,
                variables.mmc_ep_subs_speed)

        if variables.mmc_ep_subs_file_8:
            create_subs(
                variables.mmc_ep_subs_locale_8,
                variables.mmc_ep_subs_file_8,
                variables.mmc_ep_subs_type_8,
                variables.mmc_ep_subs_locale_8,
                variables.mmc_ep_subs_speed)

        if variables.mmc_ep_subs_file_9:
            create_subs(
                variables.mmc_ep_subs_locale_9,
                variables.mmc_ep_subs_file_9,
                variables.mmc_ep_subs_type_9,
                variables.mmc_ep_subs_locale_9,
                variables.mmc_ep_subs_speed)

        if variables.mmc_ep_subs_file_10:
            create_subs(
                variables.mmc_ep_subs_locale_10,
                variables.mmc_ep_subs_file_10,
                variables.mmc_ep_subs_type_10,
                variables.mmc_ep_subs_locale_10,
                variables.mmc_ep_subs_speed)

        # poster
        if variables.mmc_ep_poster_file:
            poster_comment = etree.Comment("Poster art file")
            xml_inventory.append(poster_comment)
            variables.mmc_ep_presentation_poster = "md:imageid:org:{0}:{1}:art.{2}".format(
                variables.mmc_ep_provider,
                variables.mmc_ep_season_id,
                variables.mmc_ep_poster_locale)
            xml_poster = etree.SubElement(
                xml_inventory,
                "{%s}Image" % nsmap1["manifest"],
                attrib={"ImageID": variables.mmc_ep_presentation_poster})
            with Image.open(variables.mmc_ep_poster_file_path) as im:
                width, height = im.size
            xml_poster_width = etree.SubElement(xml_poster, "{%s}Width" % nsmap1["md"])
            xml_poster_width.text = str(width)
            xml_poster_height = etree.SubElement(xml_poster, "{%s}Height" % nsmap1["md"])
            xml_poster_height.text = str(height)
            xml_poster_encoding = etree.SubElement(xml_poster, "{%s}Encoding" % nsmap1["md"])
            xml_poster_encoding.text = os.path.splitext(variables.mmc_ep_poster_file)[1].replace(".", "").lower()
            xml_poster_locale = etree.SubElement(xml_poster, "{%s}Language" % nsmap1["md"])
            xml_poster_locale.text = variables.mmc_ep_poster_locale
            xml_poster_container_ref = etree.SubElement(xml_poster, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_poster_container_loc = etree.SubElement(
                xml_poster_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_poster_container_loc.text = "file://%s" % variables.mmc_ep_poster_file

        # mmc_ep_presentations
        mmc_ep_presentations_comment = etree.Comment("Presentations")
        xml_root.append(mmc_ep_presentations_comment)
        variables.mmc_ep_presentation_id = "md:presentationid:org:{0}:{1}:feature.presentation".format(
            variables.mmc_ep_provider,
            variables.mmc_ep_id)
        xml_mmc_ep_presentations = etree.SubElement(xml_root, "{%s}Presentations" % nsmap1["manifest"])
        xml_mmc_ep_presentation = etree.SubElement(
            xml_mmc_ep_presentations,
            "{%s}Presentation" % nsmap1["manifest"],
            attrib={"PresentationID": variables.mmc_ep_presentation_id})
        xml_metadata = etree.SubElement(
            xml_mmc_ep_presentation,
            "{%s}TrackMetadata" % nsmap1["manifest"])
        xml_selection = etree.SubElement(
            xml_metadata,
            "{%s}TrackSelectionNumber" % nsmap1["manifest"])
        xml_selection.text = "0"

        mmc_ep_presentation_video_comment = etree.Comment("Video presentation")
        xml_metadata.append(mmc_ep_presentation_video_comment)
        xml_video_reference = etree.SubElement(
            xml_metadata,
            "{%s}VideoTrackReference" % nsmap1["manifest"])
        xml_video_id = etree.SubElement(
            xml_video_reference,
            "{%s}VideoTrackID" % nsmap1["manifest"])
        xml_video_id.text = variables.mmc_ep_presentation_feature

        mmc_ep_presentation_audio_main_comment = etree.Comment("Main audio presentation")
        xml_metadata.append(mmc_ep_presentation_audio_main_comment)
        xml_audio_main_reference = etree.SubElement(
            xml_metadata,
            "{%s}AudioTrackReference" % nsmap1["manifest"])
        xml_audio_main_id = etree.SubElement(
            xml_audio_main_reference,
            "{%s}AudioTrackID" % nsmap1["manifest"])
        xml_audio_main_id.text = variables.mmc_ep_presentation_audio_main

        if variables.mmc_ep_presentation_audios:
            mmc_ep_presentation_audio_comment = etree.Comment("Dub audio presentations")
            xml_metadata.append(mmc_ep_presentation_audio_comment)
            for audio in variables.mmc_ep_presentation_audios:
                xml_audio_reference = etree.SubElement(
                    xml_metadata,
                    "{%s}AudioTrackReference" % nsmap1["manifest"])
                xml_audio_id = etree.SubElement(
                    xml_audio_reference,
                    "{%s}AudioTrackID" % nsmap1["manifest"])
                xml_audio_id.text = audio

        if variables.mmc_ep_presentation_captions:
            mmc_ep_presentation_captions_comment = etree.Comment("Captions presentation")
            xml_metadata.append(mmc_ep_presentation_captions_comment)
            xml_captions_reference = etree.SubElement(
                xml_metadata,
                "{%s}SubtitleTrackReference" % nsmap1["manifest"])
            xml_captions_id = etree.SubElement(
                xml_captions_reference,
                "{%s}SubtitleTrackID" % nsmap1["manifest"])
            xml_captions_id.text = variables.mmc_ep_presentation_captions

        if variables.mmc_ep_presentation_subs:
            mmc_ep_presentation_sub_comment = etree.Comment("Subtitle presentations")
            xml_metadata.append(mmc_ep_presentation_sub_comment)
            for sub in variables.mmc_ep_presentation_subs:
                xml_subs_reference = etree.SubElement(
                    xml_metadata,
                    "{%s}SubtitleTrackReference" % nsmap1["manifest"])
                xml_subs_id = etree.SubElement(
                    xml_subs_reference,
                    "{%s}SubtitleTrackID" % nsmap1["manifest"])
                xml_subs_id.text = sub

        if variables.mmc_ep_presentation_poster:
            xml_picture_groups = etree.SubElement(xml_root, "{%s}PictureGroups" % nsmap1["manifest"])
            mmc_ep_presentation_poster_comment = etree.Comment("Poster art presentation")
            xml_picture_groups.append(mmc_ep_presentation_poster_comment)
            xml_picture_group = etree.SubElement(
                xml_picture_groups,
                "{%s}PictureGroup" % nsmap1["manifest"],
                attrib={"PictureGroupID": "md:picturegroupid:org:{0}:{1}".format(
                    variables.mmc_ep_provider,
                    variables.mmc_ep_season_id)})
            xml_picture = etree.SubElement(
                xml_picture_group,
                "{%s}Picture" % nsmap1["manifest"])
            xml_picture_id = etree.SubElement(xml_picture, "{%s}PictureID" % nsmap1["manifest"])
            xml_picture_id.text = ""
            xml_image_id = etree.SubElement(xml_picture, "{%s}ImageID" % nsmap1["manifest"])
            xml_image_id.text = variables.mmc_ep_presentation_poster

        # experiences
        experiences_comment = etree.Comment("Experiences")
        xml_root.append(experiences_comment)
        xml_experiences = etree.SubElement(xml_root, "{%s}Experiences" % nsmap1["manifest"])
        xml_experience = etree.SubElement(
            xml_experiences,
            "{%s}Experience" % nsmap1["manifest"],
            attrib={"ExperienceID": "md:experienceid:org:{0}:{1}:experience".format(
                variables.mmc_ep_provider,
                variables.mmc_ep_id),
                "version": "1.0"})
        xml_audiovisual = etree.SubElement(
            xml_experience,
            "{%s}Audiovisual" % nsmap1["manifest"],
            attrib={"ContentID": "md:cid:org:{0}:{1}".format(
                variables.mmc_ep_provider,
                variables.mmc_ep_id)})
        xml_audiovisual_type = etree.SubElement(
            xml_audiovisual,
            "{%s}Type" % nsmap1["manifest"])
        xml_audiovisual_type.text = "Main"
        xml_audiovisual_subtype = etree.SubElement(
            xml_audiovisual,
            "{%s}SubType" % nsmap1["manifest"])
        xml_audiovisual_subtype.text = "Feature"
        xml_audiovisual_id = etree.SubElement(
            xml_audiovisual,
            "{%s}PresentationID" % nsmap1["manifest"])
        xml_audiovisual_id.text = variables.mmc_ep_presentation_id

        if variables.mmc_ep_poster_file:
            xml_experience_poster = etree.SubElement(
                xml_experiences,
                "{%s}Experience" % nsmap1["manifest"],
                attrib={"ExperienceID": "md:experienceid:org:{0}:{1}:experience".format(
                    variables.mmc_ep_provider,
                    variables.mmc_ep_season_id),
                    "version": "1.0"})
            xml_experience_poster_id = etree.SubElement(
                xml_experience_poster,
                "{%s}PictureGroupID" % nsmap1["manifest"])
            xml_experience_poster_id.text = "md:picturegroupid:org:{0}:{1}".format(
                variables.mmc_ep_provider,
                variables.mmc_ep_season_id)

        # experience maps
        alid_comment = etree.Comment("Experience maps")
        xml_root.append(alid_comment)
        xml_maps = etree.SubElement(xml_root, "{%s}ALIDExperienceMaps" % nsmap1["manifest"])
        xml_map = etree.SubElement(xml_maps, "{%s}ALIDExperienceMap" % nsmap1["manifest"])
        xml_map_alid = etree.SubElement(xml_map, "{%s}ALID" % nsmap1["manifest"])
        xml_map_alid.text = "md:alid:org:{0}:{1}".format(
            variables.mmc_ep_provider,
            variables.mmc_ep_id)
        xml_map_exp_id = etree.SubElement(xml_map, "{%s}ExperienceID" % nsmap1["manifest"])
        xml_map_exp_id.text = "md:experienceid:org:{0}:{1}:experience".format(
            variables.mmc_ep_provider,
            variables.mmc_ep_id)

        if variables.mmc_ep_poster_file:
            xml_map_poster = etree.SubElement(xml_maps, "{%s}ALIDExperienceMap" % nsmap1["manifest"])
            xml_map_alid_poster = etree.SubElement(xml_map_poster, "{%s}ALID" % nsmap1["manifest"])
            xml_map_alid_poster.text = "md:alid:org:{0}:{1}".format(
                variables.mmc_ep_provider,
                variables.mmc_ep_season_id)
            xml_map_exp_id_poster = etree.SubElement(xml_map_poster, "{%s}ExperienceID" % nsmap1["manifest"])
            xml_map_exp_id_poster.text = "md:experienceid:org:{0}:{1}:experience".format(
                variables.mmc_ep_provider,
                variables.mmc_ep_season_id)

        os.chdir(os.path.dirname(variables.mmc_ep_xml_file))
        tree = etree.ElementTree(xml_root)
        tree.write(os.path.basename(variables.mmc_ep_xml_file),
                   xml_declaration=True,
                   encoding="UTF-8",
                   pretty_print=True)

    def ms_feature(self):
        nsmap1 = {
            "manifest": "http://www.movielabs.com/schema/manifest/v1.5/manifest",
            "md": "http://www.movielabs.com/schema/md/v2.4/md",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }
        schemalocation = "http://www.movielabs.com/schema/manifest/v1.5/manifest manifest-v1.5.xsd"

        xml_root = etree.Element(
            "{%s}MediaManifest" % nsmap1["manifest"],
            attrib={"{" + nsmap1["xsi"] + "}schemaLocation": schemalocation},
            nsmap=nsmap1)

        xml_compatibility = etree.SubElement(xml_root, "{%s}Compatibility" % nsmap1["manifest"])
        xml_specversion = etree.SubElement(xml_compatibility, "{%s}SpecVersion" % nsmap1["manifest"])
        xml_specversion.text = "1.5"
        xml_profile = etree.SubElement(xml_compatibility, "{%s}Profile" % nsmap1["manifest"])
        xml_profile.text = "MMC-1"

        xml_inventory = etree.SubElement(xml_root, "{%s}Inventory" % nsmap1["manifest"])

        # feature audio
        for f in self.feature:self
            audio_comment = etree.Comment("Main audio file for the feature")
            xml_inventory.append(audio_comment)
            self.presentation_audio_main = "md:audtrackid:org:{0}:{1}:feature.audio.{2}".format(
                self.provider,
                self.vendor_id,
                self.feature[f])
            xml_audio_main = etree.SubElement(
                xml_inventory,
                "{%s}Audio" % nsmap1["manifest"],
                attrib={"AudioTrackID": self.presentation_audio_main})
            xml_audio_type_main = etree.SubElement(xml_audio_main, "{%s}Type" % nsmap1["md"])
            xml_audio_type_main.text = "primary"
            xml_audio_locale_main = etree.SubElement(xml_audio_main, "{%s}Language" % nsmap1["md"])
            xml_audio_locale_main.text = self.feature[f]
            xml_audio_container_ref = etree.SubElement(xml_audio_main, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_audio_container_loc = etree.SubElement(
                xml_audio_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_audio_container_loc.text = "file://resources/%s" % f

        # feature dubs
        for index_ft_dub, ft_dub in enumerate(self.feature_dubs):
            audio_ft_dub_comment = etree.Comment("Audio dub file for the feature")
            xml_inventory.append(audio_ft_dub_comment)
            self.presentation_feature_dubs.append("md:audtrackid:org:{0}:{1}:feature.audio.{2}".format(
                self.provider,
                self.vendor_id,
                self.feature_dubs[ft_dub]))
            xml_ft_audio_dub = etree.SubElement(
                xml_inventory,
                "{%s}Audio" % nsmap1["manifest"],
                attrib={"AudioTrackID": self.presentation_feature_dubs[index_ft_dub]})
            xml_audio_type_ft_dub = etree.SubElement(xml_ft_audio_dub, "{%s}Type" % nsmap1["md"])
            xml_audio_type_ft_dub.text = "primary"
            xml_audio_locale_ft_dub = etree.SubElement(xml_ft_audio_dub, "{%s}Language" % nsmap1["md"])
            xml_audio_locale_ft_dub.text = self.feature_dubs[ft_dub]
            xml_audio_ft_dub_container_ref = etree.SubElement(xml_ft_audio_dub,
                                                              "{%s}ContainerReference" % nsmap1["manifest"])
            xml_audio_ft_dub_container_loc = etree.SubElement(
                xml_audio_ft_dub_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_audio_ft_dub_container_loc.text = "file://resources/%s" % ft_dub

        # trailer audio
        for index_tr, t in enumerate(self.trailer):
            audio_trailer_comment = etree.Comment("Audio file for the trailer")
            xml_inventory.append(audio_trailer_comment)
            self.presentation_trailer_audio.append("md:audtrackid:org:{0}:{1}:trailer.1.audio.{2}".format(
                self.provider,
                self.vendor_id,
                self.trailer[t]))
            xml_audio_trailer = etree.SubElement(
                xml_inventory,
                "{%s}Audio" % nsmap1["manifest"],
                attrib={"AudioTrackID": self.presentation_trailer_audio[index_tr]})
            xml_audio_type_trailer = etree.SubElement(xml_audio_trailer, "{%s}Type" % nsmap1["md"])
            xml_audio_type_trailer.text = "primary"
            xml_audio_locale_trailer = etree.SubElement(xml_audio_trailer, "{%s}Language" % nsmap1["md"])
            xml_audio_locale_trailer.text = self.trailer[t]
            xml_audio_trailer_container_ref = etree.SubElement(xml_audio_trailer,
                                                               "{%s}ContainerReference" % nsmap1["manifest"])
            xml_audio_trailer_container_loc = etree.SubElement(
                xml_audio_trailer_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_audio_trailer_container_loc.text = "file://resources/%s" % t

        # trailer dubs
        for index_tr_dub, tr_dub in enumerate(self.trailer_dubs):
            audio_tr_dub_comment = etree.Comment("Audio dub file for the trailer")
            xml_inventory.append(audio_tr_dub_comment)
            self.presentation_trailer_dubs.append("md:audtrackid:org:{}:{}:trailer.1.audio.{}".format(
                self.provider,
                self.vendor_id,
                self.trailer_dubs[tr_dub]
            ))
            xml_tr_audio_dub = etree.SubElement(
                xml_inventory,
                "{%s}Audio" % nsmap1["manifest"],
                attrib={"AudioTrackID": self.presentation_trailer_dubs[index_tr_dub]})
            xml_audio_type_tr_dub = etree.SubElement(xml_tr_audio_dub, "{%s}Type" % nsmap1["md"])
            xml_audio_type_tr_dub.text = "primary"
            xml_audio_locale_tr_dub = etree.SubElement(xml_tr_audio_dub, "{%s}Language" % nsmap1["md"])
            xml_audio_locale_tr_dub.text = self.trailer_dubs[tr_dub]
            xml_audio_tr_dub_container_ref = etree.SubElement(xml_tr_audio_dub,
                                                              "{%s}ContainerReference" % nsmap1["manifest"])
            xml_audio_tr_dub_container_loc = etree.SubElement(
                xml_audio_tr_dub_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_audio_tr_dub_container_loc.text = "file://resources/%s" % tr_dub

        # feature
        for f_video in self.feature:
            video_comment = etree.Comment("Video file for the feature")
            xml_inventory.append(video_comment)
            self.presentation_feature = "md:vidtrackid:org:{0}:{1}:feature.video.{2}".format(
                self.provider,
                self.vendor_id,
                self.feature[f_video])
            xml_video = etree.SubElement(
                xml_inventory,
                "{%s}Video" % nsmap1["manifest"],
                attrib={"VideoTrackID": self.presentation_feature})
            xml_video_type = etree.SubElement(xml_video, "{%s}Type" % nsmap1["md"])
            xml_video_type.text = "primary"
            xml_video_picture = etree.SubElement(xml_video, "{%s}Picture" % nsmap1["md"])
            xml_video_container_ref = etree.SubElement(xml_video, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_video_container_loc = etree.SubElement(
                xml_video_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_video_container_loc.text = "file://resources/%s" % f_video

        # trailer
        for index_t_video, t_video in enumerate(self.trailer):
            trailer_comment = etree.Comment("Video file for the trailer")
            xml_inventory.append(trailer_comment)
            self.presentation_trailer.append("md:vidtrackid:org:{}:{}:trailer.1.video.{}".format(
                self.provider,
                self.vendor_id,
                self.trailer[t_video]))
            xml_trailer = etree.SubElement(
                xml_inventory,
                "{%s}Video" % nsmap1["manifest"],
                attrib={"VideoTrackID": self.presentation_trailer[index_t_video]})
            xml_trailer_type = etree.SubElement(xml_trailer, "{%s}Type" % nsmap1["md"])
            xml_trailer_type.text = "primary"
            xml_trailer_picture = etree.SubElement(xml_trailer, "{%s}Picture" % nsmap1["md"])
            xml_trailer_container_ref = etree.SubElement(xml_trailer, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_trailer_container_loc = etree.SubElement(
                xml_trailer_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_trailer_container_loc.text = "file://resources/%s" % t_video

        # Feature Captions
        for ft_caption in self.feature_captions:
            ft_captions_comment = etree.Comment("Feature Captions")
            xml_inventory.append(ft_captions_comment)

            self.ft_presentation_captions.append("md:subtrackid:org:{0}:{1}:feature.caption.{2}".format(
                self.provider,
                self.vendor_id,
                self.feature_captions[ft_caption]))
            xml_captions = etree.SubElement(
                xml_inventory,
                "{%s}Subtitle" % nsmap1["manifest"],
                attrib={"SubtitleTrackID": "md:subtrackid:org:{0}:{1}:feature.caption.{2}".format(
                    self.provider,
                    self.vendor_id,
                    self.feature_captions[ft_caption])})
            xml_captions_type = etree.SubElement(xml_captions, "{%s}Type" % nsmap1["md"])
            xml_captions_type.text = "SDH"
            ft_captions_locale_comment = etree.Comment("Captions Language MUST be set to en-US, please verify")
            xml_captions.append(ft_captions_locale_comment)
            xml_captions_locale = etree.SubElement(xml_captions, "{%s}Language" % nsmap1["md"])
            xml_captions_locale.text = self.feature_captions[ft_caption]
            xml_captions_container_ref = etree.SubElement(
                xml_captions, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_captions_container_loc = etree.SubElement(
                xml_captions_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_captions_container_loc.text = "file://resources/%s" % ft_caption

        # Feature Full Subs
        for ft_sub_full in self.feature_full_subs:
            subs_comment = etree.Comment("Feature Full Subtitle")
            xml_inventory.append(subs_comment)

            self.ft_presentation_subs.append("md:subtrackid:org:{0}:{1}:feature.subs.{2}".format(
                self.provider,
                self.vendor_id,
                self.feature_full_subs[ft_sub_full]))
            xml_subs = etree.SubElement(
                xml_inventory,
                "{%s}Subtitle" % nsmap1["manifest"],
                attrib={"SubtitleTrackID": "md:subtrackid:org:{0}:{1}:feature.subs.{2}".format(
                    self.provider,
                    self.vendor_id,
                    self.feature_full_subs[ft_sub_full])})
            xml_subs_format = etree.SubElement(xml_subs, "{%s}Format" % nsmap1["md"])
            xml_subs_format.text = os.path.splitext(ft_sub_full)[1].replace(".", "").upper()
            xml_subs_type = etree.SubElement(xml_subs, "{%s}Type" % nsmap1["md"])
            xml_subs_type.text = "normal"
            xml_subs_locale = etree.SubElement(xml_subs, "{%s}Language" % nsmap1["md"])
            xml_subs_locale.text = self.feature_full_subs[ft_sub_full]
            xml_subs_speed = etree.SubElement(xml_subs, "{%s}Encoding" % nsmap1["md"])
            framerate, multiplier, drop = self.find_framerate(ft_sub_full)
            xml_framerate_comment = etree.Comment(
                "Subtitle framerate info: {} {} {}".format(
                    framerate,
                    multiplier,
                    drop
                ))
            xml_subs_speed.append(xml_framerate_comment)
            xml_subs_framerate = etree.SubElement(
                xml_subs_speed,
                "{%s}FrameRate" % nsmap1["md"],
                attrib={"multiplier": "1000/1001",
                        "timecode": "NonDrop"})
            xml_subs_framerate.text = "24"
            xml_subs_container_ref = etree.SubElement(
                xml_subs, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_subs_container_loc = etree.SubElement(
                xml_subs_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_subs_container_loc.text = "file://resources/%s" % ft_sub_full

        # Feature Forced Subs
        for ft_sub_forced in self.feature_forced_subs:
            subs_comment = etree.Comment("Feature Forced Subtitle")
            xml_inventory.append(subs_comment)

            self.ft_presentation_subs.append("md:subtrackid:org:{0}:{1}:feature.forced.{2}".format(
                self.provider,
                self.vendor_id,
                self.feature_forced_subs[ft_sub_forced]))
            xml_subs = etree.SubElement(
                xml_inventory,
                "{%s}Subtitle" % nsmap1["manifest"],
                attrib={"SubtitleTrackID": "md:subtrackid:org:{0}:{1}:feature.forced.{2}".format(
                    self.provider,
                    self.vendor_id,
                    self.feature_forced_subs[ft_sub_forced])})
            xml_subs_format = etree.SubElement(xml_subs, "{%s}Format" % nsmap1["md"])
            xml_subs_format.text = os.path.splitext(ft_sub_forced)[1].replace(".", "").upper()
            xml_subs_type = etree.SubElement(xml_subs, "{%s}Type" % nsmap1["md"])
            xml_subs_type.text = "forced"
            xml_subs_locale = etree.SubElement(xml_subs, "{%s}Language" % nsmap1["md"])
            xml_subs_locale.text = self.feature_forced_subs[ft_sub_forced]
            xml_subs_speed = etree.SubElement(xml_subs, "{%s}Encoding" % nsmap1["md"])
            framerate, multiplier, drop = self.find_framerate(ft_sub_forced)
            xml_framerate_comment = etree.Comment(
                "Subtitle framerate info: {} {} {}".format(
                    framerate,
                    multiplier,
                    drop
                ))
            xml_subs_speed.append(xml_framerate_comment)
            xml_subs_framerate = etree.SubElement(
                xml_subs_speed,
                "{%s}FrameRate" % nsmap1["md"],
                attrib={"multiplier": "1000/1001",
                        "timecode": "NonDrop"})
            xml_subs_framerate.text = "24"
            xml_subs_container_ref = etree.SubElement(
                xml_subs, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_subs_container_loc = etree.SubElement(
                xml_subs_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_subs_container_loc.text = "file://resources/%s" % ft_sub_forced

        # Trailer Captions
        for tr_caption in self.trailer_captions:
            tr_captions_comment = etree.Comment("Feature Captions")
            xml_inventory.append(tr_captions_comment)
            self.tr_presentation_captions.append("md:subtrackid:org:{0}:{1}:trailer.1.caption.{2}".format(
                self.provider,
                self.vendor_id,
                self.trailer_captions[tr_caption]))
            xml_tr_captions = etree.SubElement(
                xml_inventory,
                "{%s}Subtitle" % nsmap1["manifest"],
                attrib={"SubtitleTrackID": "md:subtrackid:org:{0}:{1}:trailer.1.caption.{2}".format(
                    self.provider,
                    self.vendor_id,
                    self.trailer_captions[tr_caption])})
            xml_tr_captions_type = etree.SubElement(xml_tr_captions, "{%s}Type" % nsmap1["md"])
            xml_tr_captions_type.text = "SDH"
            tr_captions_locale_comment = etree.Comment("Captions Language MUST be set to en-US, please verify")
            xml_tr_captions.append(tr_captions_locale_comment)
            xml_tr_captions_locale = etree.SubElement(xml_tr_captions, "{%s}Language" % nsmap1["md"])
            xml_tr_captions_locale.text = self.trailer_captions[tr_caption]
            xml_tr_captions_container_ref = etree.SubElement(
                xml_tr_captions, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_tr_captions_container_loc = etree.SubElement(
                xml_tr_captions_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_tr_captions_container_loc.text = "file://resources/%s" % tr_caption

        # Trailer Full Subs
        for tr_sub_full in self.trailer_full_subs:
            subs_comment = etree.Comment("Trailer Full Subtitle")
            xml_inventory.append(subs_comment)

            self.tr_presentation_subs.append("md:subtrackid:org:{}:{}:trailer.1.subs.{}".format(
                self.provider,
                self.vendor_id,
                self.trailer_full_subs[tr_sub_full]))
            xml_subs = etree.SubElement(
                xml_inventory,
                "{%s}Subtitle" % nsmap1["manifest"],
                attrib={"SubtitleTrackID": "md:subtrackid:org:{}:{}:trailer.1.subs.{}".format(
                    self.provider,
                    self.vendor_id,
                    self.trailer_full_subs[tr_sub_full])})
            xml_subs_format = etree.SubElement(xml_subs, "{%s}Format" % nsmap1["md"])
            xml_subs_format.text = os.path.splitext(tr_sub_full)[1].replace(".", "").upper()
            xml_subs_type = etree.SubElement(xml_subs, "{%s}Type" % nsmap1["md"])
            xml_subs_type.text = "normal"
            xml_subs_locale = etree.SubElement(xml_subs, "{%s}Language" % nsmap1["md"])
            xml_subs_locale.text = self.trailer_full_subs[tr_sub_full]
            xml_subs_speed = etree.SubElement(xml_subs, "{%s}Encoding" % nsmap1["md"])
            framerate, multiplier, drop = self.find_framerate(tr_sub_full)
            xml_framerate_comment = etree.Comment(
                "Subtitle framerate info: {} {} {}".format(
                    framerate,
                    multiplier,
                    drop
                ))
            xml_subs_speed.append(xml_framerate_comment)
            xml_subs_framerate = etree.SubElement(
                xml_subs_speed,
                "{%s}FrameRate" % nsmap1["md"],
                attrib={"multiplier": "1000/1001",
                        "timecode": "NonDrop"})
            xml_subs_framerate.text = "24"
            xml_subs_container_ref = etree.SubElement(
                xml_subs, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_subs_container_loc = etree.SubElement(
                xml_subs_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_subs_container_loc.text = "file://resources/%s" % tr_sub_full

        # Trailer Forced Subs
        for tr_sub_forced in self.trailer_forced_subs:
            subs_comment = etree.Comment("Trailer Forced Subtitle")
            xml_inventory.append(subs_comment)

            self.tr_presentation_subs.append("md:subtrackid:org:{}:{}:trailer.1.subs.{}".format(
                self.provider,
                self.vendor_id,
                self.trailer_forced_subs[tr_sub_forced]))
            xml_subs = etree.SubElement(
                xml_inventory,
                "{%s}Subtitle" % nsmap1["manifest"],
                attrib={"SubtitleTrackID": "md:subtrackid:org:{}:{}:trailer.1.subs.{}".format(
                    self.provider,
                    self.vendor_id,
                    self.trailer_forced_subs[tr_sub_forced])})
            xml_subs_format = etree.SubElement(xml_subs, "{%s}Format" % nsmap1["md"])
            xml_subs_format.text = os.path.splitext(tr_sub_forced)[1].replace(".", "").upper()
            xml_subs_type = etree.SubElement(xml_subs, "{%s}Type" % nsmap1["md"])
            xml_subs_type.text = "forced"
            xml_subs_locale = etree.SubElement(xml_subs, "{%s}Language" % nsmap1["md"])
            xml_subs_locale.text = self.trailer_forced_subs[tr_sub_forced]
            xml_subs_speed = etree.SubElement(xml_subs, "{%s}Encoding" % nsmap1["md"])
            framerate, multiplier, drop = self.find_framerate(tr_sub_forced)
            xml_framerate_comment = etree.Comment(
                "Subtitle framerate info: {} {} {}".format(
                    framerate,
                    multiplier,
                    drop
                ))
            xml_subs_speed.append(xml_framerate_comment)
            xml_subs_framerate = etree.SubElement(
                xml_subs_speed,
                "{%s}FrameRate" % nsmap1["md"],
                attrib={"multiplier": "1000/1001",
                        "timecode": "NonDrop"})
            xml_subs_framerate.text = "24"
            xml_subs_container_ref = etree.SubElement(
                xml_subs, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_subs_container_loc = etree.SubElement(
                xml_subs_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_subs_container_loc.text = "file://resources/%s" % tr_sub_forced

        # Poster art
        for p in self.poster:
            poster_comment = etree.Comment("Poster art file")
            xml_inventory.append(poster_comment)
            self.presentation_poster.append("md:imageid:org:{0}:{1}:art.{2}".format(
                self.provider,
                self.vendor_id,
                self.poster[p]))
            xml_poster = etree.SubElement(
                xml_inventory,
                "{%s}Image" % nsmap1["manifest"],
                attrib={"ImageID": "md:imageid:org:{0}:{1}:art.{2}".format(
                    self.provider,
                    self.vendor_id,
                    self.poster[p])})
            with Image.open(os.path.join(self.package_path + os.sep, p)) as im:
                width, height = im.size
            xml_poster_width = etree.SubElement(xml_poster, "{%s}Width" % nsmap1["md"])
            xml_poster_width.text = str(width)
            xml_poster_height = etree.SubElement(xml_poster, "{%s}Height" % nsmap1["md"])
            xml_poster_height.text = str(height)
            xml_poster_encoding = etree.SubElement(xml_poster, "{%s}Encoding" % nsmap1["md"])
            xml_poster_encoding.text = os.path.splitext(p)[1].replace(".", "").lower()
            xml_poster_locale = etree.SubElement(xml_poster, "{%s}Language" % nsmap1["md"])
            xml_poster_locale.text = self.poster[p]
            xml_poster_container_ref = etree.SubElement(xml_poster, "{%s}ContainerReference" % nsmap1["manifest"])
            xml_poster_container_loc = etree.SubElement(
                xml_poster_container_ref,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_poster_container_loc.text = "file://resources/%s" % p

        # Metadata Reference
        metadata_comment = etree.Comment("Metadata Reference")
        xml_inventory.append(metadata_comment)
        xml_metadata = etree.SubElement(
            xml_inventory,
            "{%s}Metadata" % nsmap1["manifest"],
            attrib={
                "ContentID": "md:cid:org:{}:{}_en_MEC-movie".format(
                    self.provider, self.vendor_id)})
        xml_container_reference = etree.SubElement(
            xml_metadata,
            "{%s}ContainerReference" % nsmap1["manifest"],
            attrib={
                "type": "common"})

        # check if the xml file exists
        try:
            movie_xml = [x for x in self.xml if "movie" in x.lower()][0]

        except IndexError:
            movie_xml_comment = etree.Comment("Please enter the name of the movie metadata file")
            xml_container_reference.append(movie_xml_comment)
            xml_container_location = etree.SubElement(
                xml_container_reference,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_container_location.text = "file://resources/"

        else:
            xml_container_location = etree.SubElement(
                xml_container_reference,
                "{%s}ContainerLocation" % nsmap1["manifest"])
            xml_container_location.text = "file://resources/{}".format(movie_xml)

        for t in self.trailer:
            xml_metadata = etree.SubElement(
                xml_inventory,
                "{%s}Metadata" % nsmap1["manifest"],
                attrib={
                    "ContentID": "md:cid:org:{}:{}_en_MEC-Trailer1:trailer.1".format(
                        self.provider,
                        self.vendor_id)})
            xml_container_reference = etree.SubElement(
                xml_metadata,
                "{%s}ContainerReference" % nsmap1["manifest"],
                attrib={
                    "type": "common"})

            # check if the xml file exists
            try:
                trailer_xml = [x for x in self.xml if "trailer" in x.lower()][0]

            except IndexError:
                trailer_xml_comment = etree.Comment("Please enter the name of the trailer metadata file")
                xml_container_reference.append(trailer_xml_comment)
                xml_container_location = etree.SubElement(
                    xml_container_reference,
                    "{%s}ContainerLocation" % nsmap1["manifest"])
                xml_container_location.text = "file://resources/"

            else:
                xml_container_location = etree.SubElement(
                    xml_container_reference,
                    "{%s}ContainerLocation" % nsmap1["manifest"])
                xml_container_location.text = "file://resources/{}".format(trailer_xml)

        # presentations
        mmc_ft_presentations_comment = etree.Comment("Presentations")
        xml_root.append(mmc_ft_presentations_comment)
        self.ft_presentation_feature_id = "md:presentationid:org:{0}:{1}:feature.presentation".format(
            self.provider,
            self.vendor_id)

        for i in self.trailer:
            self.ft_presentation_trailer_id.append("md:presentationid:org:{}:{}:trailer.1.presentation".format(
                self.provider,
                self.vendor_id
            ))
        xml_mmc_presentations = etree.SubElement(xml_root, "{%s}Presentations" % nsmap1["manifest"])

        # feature presentation
        xml_feature_presentation = etree.SubElement(
            xml_mmc_presentations, "{%s}Presentation" % nsmap1["manifest"],
            attrib={"PresentationID": self.ft_presentation_feature_id}
        )
        xml_metadata_feature = etree.SubElement(
            xml_feature_presentation,
            "{%s}TrackMetadata" % nsmap1["manifest"])
        xml_selection = etree.SubElement(
            xml_metadata_feature,
            "{%s}TrackSelectionNumber" % nsmap1["manifest"])
        xml_selection.text = "0"

        xml_ft_present_comment = etree.Comment("Feature video presentation")
        xml_metadata_feature.append(xml_ft_present_comment)
        xml_feature_reference = etree.SubElement(
            xml_metadata_feature,
            "{%s}VideoTrackReference" % nsmap1["manifest"])
        xml_feature_id = etree.SubElement(
            xml_feature_reference,
            "{%s}VideoTrackID" % nsmap1["manifest"])
        xml_feature_id.text = self.presentation_feature

        xml_ft_present_audio_main_comment = etree.Comment("Feature main audio presentation")
        xml_metadata_feature.append(xml_ft_present_audio_main_comment)
        xml_audio_main_reference = etree.SubElement(
            xml_metadata_feature,
            "{%s}AudioTrackReference" % nsmap1["manifest"])
        xml_audio_main_id = etree.SubElement(
            xml_audio_main_reference,
            "{%s}AudioTrackID" % nsmap1["manifest"])
        xml_audio_main_id.text = self.presentation_audio_main

        for ft_dubs_i in self.presentation_feature_dubs:
            xml_ft_present_audio_dub_comment = etree.Comment("Feature dub audio presentation")
            xml_metadata_feature.append(xml_ft_present_audio_dub_comment)
            xml_audio_main_reference = etree.SubElement(
                xml_metadata_feature,
                "{%s}AudioTrackReference" % nsmap1["manifest"])
            xml_audio_main_id = etree.SubElement(
                xml_audio_main_reference,
                "{%s}AudioTrackID" % nsmap1["manifest"])
            xml_audio_main_id.text = ft_dubs_i

        for ft_caption_i in self.ft_presentation_captions:
            mmc_ft_presentation_caption_comment = etree.Comment("Feature captions presentation")
            xml_metadata_feature.append(mmc_ft_presentation_caption_comment)
            xml_caption_reference = etree.SubElement(
                xml_metadata_feature,
                "{%s}SubtitleTrackReference" % nsmap1["manifest"])
            xml_captions_id = etree.SubElement(
                xml_caption_reference,
                "{%s}SubtitleTrackID" % nsmap1["manifest"])
            xml_captions_id.text = ft_caption_i

        for ft_subs_i in self.ft_presentation_subs:
            mmc_ft_presentation_sub_comment = etree.Comment("Feature subtitle presentation")
            xml_metadata_feature.append(mmc_ft_presentation_sub_comment)
            xml_subs_reference = etree.SubElement(
                xml_metadata_feature,
                "{%s}SubtitleTrackReference" % nsmap1["manifest"])
            xml_subs_id = etree.SubElement(
                xml_subs_reference,
                "{%s}SubtitleTrackID" % nsmap1["manifest"])
            xml_subs_id.text = ft_subs_i

        # trailer presentations
        for index_present_tr, tr_present_i in enumerate(self.ft_presentation_trailer_id):
            xml_trailer_presentation = etree.SubElement(
                xml_mmc_presentations, "{%s}Presentation" % nsmap1["manifest"],
                attrib={"PresentationID": tr_present_i}
            )
            xml_metadata_trailer = etree.SubElement(
                xml_trailer_presentation,
                "{%s}TrackMetadata" % nsmap1["manifest"])
            xml_selection_tr = etree.SubElement(
                xml_metadata_trailer,
                "{%s}TrackSelectionNumber" % nsmap1["manifest"])
            xml_selection_tr.text = "0"

            xml_tr_present_comment = etree.Comment("Trailer {} video presentation".format(
                index_present_tr + 1
            ))
            xml_metadata_trailer.append(xml_tr_present_comment)
            xml_trailer_reference = etree.SubElement(
                xml_metadata_trailer,
                "{%s}VideoTrackReference" % nsmap1["manifest"])
            xml_trailer_id = etree.SubElement(
                xml_trailer_reference,
                "{%s}VideoTrackID" % nsmap1["manifest"])
            xml_trailer_id.text = self.presentation_trailer[index_present_tr]

            xml_tr_present_audio_comment = etree.Comment("Trailer {} audio presentation".format(
                index_present_tr + 1
            ))
            xml_metadata_trailer.append(xml_tr_present_audio_comment)
            xml_audio_tr_reference = etree.SubElement(
                xml_metadata_trailer,
                "{%s}AudioTrackReference" % nsmap1["manifest"])
            xml_audio_tr_id = etree.SubElement(
                xml_audio_tr_reference,
                "{%s}AudioTrackID" % nsmap1["manifest"])
            xml_audio_tr_id.text = self.presentation_trailer_audio[index_present_tr]

            for tr_dubs_i in self.presentation_trailer_dubs:
                xml_tr_present_audio_dub_comment = etree.Comment("Trailer {} audio dub presentation".format(
                    index_present_tr + 1
                ))
                xml_metadata_trailer.append(xml_tr_present_audio_dub_comment)
                xml_audio_tr_reference = etree.SubElement(
                    xml_metadata_trailer,
                    "{%s}AudioTrackReference" % nsmap1["manifest"])
                xml_audio_tr_id = etree.SubElement(
                    xml_audio_tr_reference,
                    "{%s}AudioTrackID" % nsmap1["manifest"])
                xml_audio_tr_id.text = tr_dubs_i

            for tr_caption_i in self.tr_presentation_captions:
                mmc_tr_presentation_caption_comment = etree.Comment("Trailer captions presentation")
                xml_metadata_trailer.append(mmc_tr_presentation_caption_comment)
                xml_tr_caption_reference = etree.SubElement(
                    xml_metadata_trailer,
                    "{%s}SubtitleTrackReference" % nsmap1["manifest"])
                xml_tr_captions_id = etree.SubElement(
                    xml_tr_caption_reference,
                    "{%s}SubtitleTrackID" % nsmap1["manifest"])
                xml_tr_captions_id.text = tr_caption_i

            for tr_subs_i in self.tr_presentation_subs:
                mmc_tr_presentation_sub_comment = etree.Comment("Trailer {} subtitle presentation".format(
                    index_present_tr + 1
                ))
                xml_metadata_trailer.append(mmc_tr_presentation_sub_comment)
                xml_tr_subs_reference = etree.SubElement(
                    xml_metadata_trailer,
                    "{%s}SubtitleTrackReference" % nsmap1["manifest"])
                xml_tr_subs_id = etree.SubElement(
                    xml_tr_subs_reference,
                    "{%s}SubtitleTrackID" % nsmap1["manifest"])
                xml_tr_subs_id.text = tr_subs_i

        # Experiences
        xml_experiences = etree.SubElement(xml_root, "{%s}Experiences" % nsmap1["manifest"])

        # Feature experience
        xml_ft_experience_id = etree.SubElement(
            xml_experiences,
            "{%s}Experience" % nsmap1["manifest"],
            attrib={"ExperienceID": "md:experienceid:org:{}:{}:experience".format(
                self.provider,
                self.vendor_id
            ),
                "version": "1.0"}
        )
        for region in self.territories:
            xml_ft_region = etree.SubElement(xml_ft_experience_id, "{%s}Region" % nsmap1["manifest"])
            xml_ft_country = etree.SubElement(xml_ft_region, "{%s}country" % nsmap1["md"])
            xml_ft_country.text = region

        xml_ft_content_id = etree.SubElement(xml_ft_experience_id, "{%s}ContentID" % nsmap1["manifest"])
        xml_ft_content_id.text = "md:cid:org:{}:{}_en_MEC-movie".format(self.provider, self.vendor_id)
        xml_ft_audiovisual = etree.SubElement(
            xml_ft_experience_id,
            "{%s}Audiovisual" % nsmap1["manifest"],
            attrib={"ContentID": "md:cid:org:{}:{}_en_MEC-movie".format(self.provider, self.vendor_id)})
        xml_ft_type = etree.SubElement(xml_ft_audiovisual, "{%s}Type" % nsmap1["manifest"])
        xml_ft_type.text = "Main"
        xml_ft_subtype = etree.SubElement(xml_ft_audiovisual, "{%s}SubType" % nsmap1["manifest"])
        xml_ft_subtype.text = "Feature"
        xml_ft_present_id = etree.SubElement(xml_ft_audiovisual, "{%s}PresentationID" % nsmap1["manifest"])
        xml_ft_present_id.text = "md:presentationid:org:{}:{}:feature.presentation".format(
            self.provider, self.vendor_id)

        for tr_i in self.trailer:
            xml_ft_exp_child = etree.SubElement(xml_ft_experience_id, "{%s}ExperienceChild" % nsmap1["manifest"])
            xml_ft_relation = etree.SubElement(xml_ft_exp_child, "{%s}Relationship" % nsmap1["manifest"])
            xml_ft_relation.text = "ispromotionfor"
            xml_experience_id_child = etree.SubElement(xml_ft_exp_child, "{%s}ExperienceID" % nsmap1["manifest"])
            xml_experience_id_child.text = "md:presentationid:org:{}:{}:trailer.1.presentation".format(
                self.provider, self.vendor_id)

        # Trailer experiences
        for tr_exp in self.trailer:
            xml_tr_experience_id = etree.SubElement(
                xml_experiences,
                "{%s}Experience" % nsmap1["manifest"],
                attrib={"ExperienceID": "md:experienceid:org:{}:{}:trailer.1.experience".format(
                    self.provider,
                    self.vendor_id),
                    "version": "1.0"}
            )
            for region in self.territories:
                xml_tr_region = etree.SubElement(xml_tr_experience_id, "{%s}Region" % nsmap1["manifest"])
                xml_tr_country = etree.SubElement(xml_tr_region, "{%s}country" % nsmap1["md"])
                xml_tr_country.text = region

            xml_tr_content_id = etree.SubElement(xml_tr_experience_id, "{%s}ContentID" % nsmap1["manifest"])
            xml_tr_content_id.text = "md:cid:org:{}:{}_en_MEC-Trailer1:trailer.1".format(
                self.provider,
                self.vendor_id)
            xml_tr_audiovisual = etree.SubElement(
                xml_tr_experience_id,
                "{%s}Audiovisual" % nsmap1["manifest"],
                attrib={"ContentID": "md:cid:org:{}:{}_en_MEC-Trailer1:trailer.1".format(
                    self.provider,
                    self.vendor_id)})
            xml_tr_type = etree.SubElement(xml_tr_audiovisual, "{%s}Type" % nsmap1["manifest"])
            xml_tr_type.text = "Promotion"
            xml_tr_subtype = etree.SubElement(xml_tr_audiovisual, "{%s}SubType" % nsmap1["manifest"])
            xml_tr_subtype.text = "Default Trailer"
            xml_tr_present_id = etree.SubElement(xml_tr_audiovisual, "{%s}PresentationID" % nsmap1["manifest"])
            xml_tr_present_id.text = "md:presentationid:org:{}:{}:trailer.1.presentation".format(
                self.provider, self.vendor_id)

        # ALID maps
        xml_alid_maps = etree.SubElement(xml_root, "{%s}ALIDExperienceMaps" % nsmap1["manifest"])
        xml_alid_map = etree.SubElement(xml_alid_maps, "{%s}ALIDExperienceMap" % nsmap1["manifest"])
        xml_alid = etree.SubElement(xml_alid_map, "{%s}ALID" % nsmap1["manifest"])
        xml_alid.text = self.vendor_id
        xml_alid_exp_id = etree.SubElement(xml_alid_map, "{%s}ExperienceID" % nsmap1["manifest"])
        xml_alid_exp_id.text = "md:experienceid:org:{}:{}".format(self.provider, self.vendor_id)

        tree = etree.ElementTree(xml_root)
        tree.write(
            os.path.join(
                os.path.dirname(self.package_path) + os.sep,
                "{}-Manifest_{}.xml".format(
                    self.provider,
                    datetime.datetime.now().strftime("%Y-%m-%d"))),
            xml_declaration=True,
            encoding="UTF-8",
            pretty_print=True)
