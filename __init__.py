# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Bob Swift (rdswift)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

# pylint: disable=import-error
# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=no-name-in-module

from collections import namedtuple

from PyQt6 import QtWidgets

from picard.config import get_config
from picard.plugin3.api import (
    OptionsPage,
    PluginApi,
    t_,
)

from .ui_options_combine_performer_tags import \
    Ui_CombinePerformerTagsOptionsPage


USER_GUIDE_URL = 'https://picard-plugins-user-guides.readthedocs.io/en/latest/combine_performer_tags/user_guide.html'


class PluginOptions():
    """Tag formatting options used by the plugin.  Initial attribute values
    are the key strings for the options settings in the Picard configuration.
    """
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    # pylint: disable=invalid-name

    def __init__(self, api: PluginApi = None) -> None:
        self.OPT_CREDITED_ARTIST = 'cred_artist'
        self.OPT_CREDITED_INSTRUMENT = 'cred_instrument'
        self.OPT_CREDITED_VOCAL = 'cred_vocal'
        self.OPT_INSTRUMENT_ATTR_ADDITIONAL = 'inst_attr_additional'
        self.OPT_INSTRUMENT_ATTR_GUEST = 'inst_attr_guest'
        self.OPT_INSTRUMENT_ATTR_SOLO = 'inst_attr_solo'
        self.OPT_VOCAL_ATTR_ADDITIONAL = 'vocal_attr_additional'
        self.OPT_VOCAL_ATTR_GUEST = 'vocal_attr_guest'
        self.OPT_VOCAL_ATTR_SOLO = 'vocal_attr_solo'
        self.OPT_VOCAL_ATTR_TYPES = 'vocal_attr_types'
        self.OPT_TAG_GROUP_BY_ARTIST = 'group_by_artist'
        self.OPT_FORMAT_GROUP_ADDITIONAL = 'format_group_additional'
        self.OPT_FORMAT_GROUP_GUEST = 'format_group_guest'
        self.OPT_FORMAT_GROUP_SOLO = 'format_group_solo'
        self.OPT_FORMAT_GROUP_VOCALS = 'format_group_vocals'
        self.OPT_FORMAT_GROUP_1_START = 'format_group_1_start_char'
        self.OPT_FORMAT_GROUP_1_END = 'format_group_1_end_char'
        self.OPT_FORMAT_GROUP_1_SEP = 'format_group_1_sep_char'
        self.OPT_FORMAT_GROUP_2_START = 'format_group_2_start_char'
        self.OPT_FORMAT_GROUP_2_END = 'format_group_2_end_char'
        self.OPT_FORMAT_GROUP_2_SEP = 'format_group_2_sep_char'
        self.OPT_FORMAT_GROUP_3_START = 'format_group_3_start_char'
        self.OPT_FORMAT_GROUP_3_END = 'format_group_3_end_char'
        self.OPT_FORMAT_GROUP_3_SEP = 'format_group_3_sep_char'
        self.OPT_FORMAT_GROUP_4_START = 'format_group_4_start_char'
        self.OPT_FORMAT_GROUP_4_END = 'format_group_4_end_char'
        self.OPT_FORMAT_GROUP_4_SEP = 'format_group_4_sep_char'

        self.api = api

    def load_from_config(self) -> None:
        """Set the current attributes from the Picard configuration settings.
        """
        temp = PluginOptions(self.api)  # Get unintialized list to provide Picard option settings keys
        for option in [x for x in temp.__dict__ if x.startswith('OPT_')]:
            key = getattr(temp, option)
            self.__dict__[option] = self.api.plugin_config[key]


class CombinePerformerTags():
    """Combines performer information from the metadata to produce a multi-value variable.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, source_metadata: dict, options: PluginOptions = None, api: PluginApi = None) -> None:
        """Combines performer information from the metadata to produce a multi-value variable.

        Args:
            source_metadata (dict): Metadata to process.
            options (PluginOptions, optional): Options to use for processing.  If not provided,
                the current settings from Picard's option settings are used.
            api (PluginApi, optional): The plugin's api.  Defaults to None.
        """
        self.performance_dict = {}
        self.source = source_metadata
        if options:
            self.settings = options
        else:
            self.settings = PluginOptions(api)
            self.settings.load_from_config()

    def _make_instrument_key(self, instrument: str, groups: dict) -> str:
        key = ''

        if groups[1]:
            sep: str = self.settings.OPT_FORMAT_GROUP_1_SEP if self.settings.OPT_FORMAT_GROUP_1_SEP else ' '
            key += self.settings.OPT_FORMAT_GROUP_1_START + sep.join(groups[1]) + self.settings.OPT_FORMAT_GROUP_1_END

        key += instrument

        if groups[2]:
            sep: str = self.settings.OPT_FORMAT_GROUP_2_SEP if self.settings.OPT_FORMAT_GROUP_2_SEP else ' '
            key += self.settings.OPT_FORMAT_GROUP_2_START + sep.join(groups[2]) + self.settings.OPT_FORMAT_GROUP_2_END

        if groups[3]:
            sep: str = self.settings.OPT_FORMAT_GROUP_3_SEP if self.settings.OPT_FORMAT_GROUP_3_SEP else ' '
            key += self.settings.OPT_FORMAT_GROUP_3_START + sep.join(groups[3]) + self.settings.OPT_FORMAT_GROUP_3_END

        return key

    def _make_instrument_value(self, instrument: str, groups: dict) -> str:
        value = ''

        if groups[1]:
            sep: str = self.settings.OPT_FORMAT_GROUP_1_SEP if self.settings.OPT_FORMAT_GROUP_1_SEP else ' '
            value += self.settings.OPT_FORMAT_GROUP_1_START + sep.join(groups[1]) + self.settings.OPT_FORMAT_GROUP_1_END

        value += instrument

        if groups[2]:
            sep: str = self.settings.OPT_FORMAT_GROUP_2_SEP if self.settings.OPT_FORMAT_GROUP_2_SEP else ' '
            value += self.settings.OPT_FORMAT_GROUP_2_START + sep.join(groups[2]) + self.settings.OPT_FORMAT_GROUP_2_END

        if groups[3]:
            sep: str = self.settings.OPT_FORMAT_GROUP_3_SEP if self.settings.OPT_FORMAT_GROUP_3_SEP else ' '
            value += self.settings.OPT_FORMAT_GROUP_3_START + sep.join(groups[3]) + self.settings.OPT_FORMAT_GROUP_3_END

        if groups[4]:
            sep: str = self.settings.OPT_FORMAT_GROUP_4_SEP if self.settings.OPT_FORMAT_GROUP_4_SEP else ' '
            value += self.settings.OPT_FORMAT_GROUP_4_START + sep.join(groups[4]) + self.settings.OPT_FORMAT_GROUP_4_END

        return value

    def _make_artist_value(self, artist: str, groups: dict) -> str:
        value = artist

        if groups[4]:
            sep: str = self.settings.OPT_FORMAT_GROUP_4_SEP if self.settings.OPT_FORMAT_GROUP_4_SEP else ' '
            value += self.settings.OPT_FORMAT_GROUP_4_START + sep.join(groups[4]) + self.settings.OPT_FORMAT_GROUP_4_END

        return value

    def _parse_metadata(self, relation: dict) -> tuple:
        # pylint: disable=too-many-boolean-expressions
        # pylint: disable=too-many-branches
        groups = {1: [], 2: [], 3: [], 4: []}

        group = relation['type'][0]
        attributes = set(x for x in relation['attributes'])   # Make copy to update if empty
        performer = relation['target-credit'] if self.settings.OPT_CREDITED_ARTIST and relation['target-credit'] else relation['artist']['name']
        performer_sort = relation['artist']['sort-name']
        if not attributes or not attributes.difference({'additional', 'guest', 'solo'}):
            attributes.add('vocals' if group == 'v' else 'instruments')
        instrument = attributes.difference({'additional', 'guest', 'solo'}).pop()
        attributes = attributes.difference({instrument,})

        # Get as credited name for the instrument or vocal
        if (
            'attribute-credits' in relation and instrument in relation['attribute-credits']
            and (
                (group == 'i' and self.settings.OPT_CREDITED_INSTRUMENT)
                or (group == 'v' and self.settings.OPT_CREDITED_VOCAL)
            )
        ):
            instrument = relation['attribute-credits'][instrument]

        # Add any additional attributes such as 'guest' or 'solo'
        for attr in attributes:
            if (
                attr == 'additional'
                and (
                    (group == 'i' and not self.settings.OPT_INSTRUMENT_ATTR_ADDITIONAL)
                    or (group == 'v' and not self.settings.OPT_VOCAL_ATTR_ADDITIONAL)
                )
            ):
                continue

            if (
                attr == 'guest'
                and (
                    (group == 'i' and not self.settings.OPT_INSTRUMENT_ATTR_GUEST)
                    or (group == 'v' and not self.settings.OPT_VOCAL_ATTR_GUEST)
                )
            ):
                continue

            if (
                attr == 'solo'
                and (
                    (group == 'i' and not self.settings.OPT_INSTRUMENT_ATTR_SOLO)
                    or (group == 'v' and not self.settings.OPT_VOCAL_ATTR_SOLO)
                )
            ):
                continue

            if attr == 'additional':
                groups[self.settings.OPT_FORMAT_GROUP_ADDITIONAL].append(attr)
            elif attr == 'guest':
                groups[self.settings.OPT_FORMAT_GROUP_GUEST].append(attr)
            elif attr == 'solo':
                groups[self.settings.OPT_FORMAT_GROUP_SOLO].append(attr)
            elif self.settings.OPT_VOCAL_ATTR_TYPES and group == 'v':
                groups[self.settings.OPT_FORMAT_GROUP_VOCALS].append(attr)

        #############################################################
        #                                                           #
        #   Grouping Rules                                          #
        #                                                           #
        #   If grouping by artist:                                  #
        #       - keys are sorted by artist sort name               #
        #       - values are sorted by instrument/vocal name with   #
        #         instruments appearing before vocals               #
        #                                                           #
        #   If grouping by instrument/vocal                         #
        #       - keys are sorted by instrument/vocal name with     #
        #         instruments appearing before vocals               #
        #       - values are sorted by artist sort name             #
        #                                                           #
        #############################################################

        if self.settings.OPT_TAG_GROUP_BY_ARTIST:
            key = performer
            value = self._make_instrument_value(instrument, groups)
            sort_key = performer_sort
            sort_value = group + value
        else:
            key = self._make_instrument_key(instrument, groups)
            value = self._make_artist_value(performer, groups)
            sort_key = group + key
            sort_value = performer_sort

        return key, value, group, sort_key, sort_value

    def get_performers(self) -> list:
        """Process the input metadata using the provided settings to produce
        the list of performance items for the multi-value variable.

        Returns:
            list: Performance items for the multi-value variable.
        """
        # pylint: disable=too-many-boolean-expressions

        performers = {}
        performers_tag = []

        PerformerInfo = namedtuple('PerformerInfo', ['value_sort', 'info'])

        for relation in self.source:
            if (
                'artist' not in relation or not relation['artist']
                or 'type' not in relation or relation['type'] not in ('instrument', 'vocal')
            ):
                continue

            key, value, group, sort_key, sort_value = self._parse_metadata(relation)
            if not key or not len(value) > 1:
                continue

            if key not in performers:
                performers[key] = {'group': 'z', 'key_sort': '', 'data': set(), }

            if group < performers[key]['group']:
                performers[key]['group'] = group

            performers[key]['key_sort'] = sort_key
            performers[key]['data'].add(PerformerInfo(sort_value, value))

        for item in sorted(performers.items(), key=lambda x: x[1]['group'] + x[1]['key_sort']):
            tag_key = item[0]
            values = [x[1] for x in sorted(item[1]['data'], key=lambda y: y[0])]
            value = ', '.join(values)
            performers_tag.append(f"{tag_key}: {value}")

        return performers_tag


def combine_performer_tags(api: PluginApi, _album, album_metadata, track_metadata, release_metadata) -> None:
    """Combines performer information into a multi-value variable for use in scripting.
    """

    def metadata_error(album_id: str, metadata_element: str, track_number: str) -> None:
        api.logger.error(f"{album_id}: Missing '{metadata_element}' in track {track_number} metadata.")

    if not api.global_config.setting['track_ars']:
        api.logger.error("Use track relationships is not enabled in Options -> Metadata.")
        return

    album_id = release_metadata['id'] if release_metadata else 'No Album ID'
    track_number = track_metadata['number'] if track_metadata and 'number' in track_metadata else 'No Track Number'

    if 'recording' not in track_metadata:
        metadata_error(album_id, 'recording', track_number)
        return

    if 'relations' not in track_metadata['recording']:
        metadata_error(album_id, 'recording->relations', track_number)
        return

    processor = CombinePerformerTags(track_metadata['recording']['relations'], api=api)
    album_metadata['~performers'] = processor.get_performers()


class CombinePerformerTagsOptionsPage(OptionsPage):
    """Options page for the Combine Performer Tags plugin.
    """

    TITLE = t_("ui.title", "Combine Performer Tags")

    keys = PluginOptions()  # Get unintialized list to provide Picard option settings keys

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_CombinePerformerTagsOptionsPage()
        self.ui.setupUi(self)

        # Add translations
        self.ui.label_20.setText(self.api.tr('ui.page_title', "Combine Performer Tags"))
        self.ui.format_description.setText(
            self.api.tr(
                "ui.format_description",
                (
                    "<html><head/><body><p>These settings will determine how the <span style=\"font-weight:600;\">"
                    "Combine Performer Tags</span> plugin operates. Note that there is an example output displayed at "
                    "the bottom of this settings window, and the example is updated whenever a setting is changed.</p><p>"
                    "Please see the <a href=\"{url}\"><span style=\"text-decoration: underline; color:#0000ff;\">User "
                    "Guide</span></a> for additional information.</p></body></html>"
                )
            ).format(url=USER_GUIDE_URL)
        )
        self.ui.label_21.setText(self.api.tr("ui.standard_or_credited", "Standard or Credited Information"))
        self.ui.label.setText(
            self.api.tr(
                "ui.standard_or_credited_description",
                (
                    "<html><head/><body><p>These options determine whether the information is displayed as <span style=\""
                    "font-weight:600;\">credited</span> or <span style=\"font-weight:600;\">standard</span>. If credited is "
                    "selected for one of the information types and there is no credited value available, the standard "
                    "information will be used.</p></body></html>"
                )
            )
        )
        self.ui.cb_credited_artists.setText(self.api.tr("ui.cb_credited_artists", "As credited artist names"))
        self.ui.cb_credited_instruments.setText(self.api.tr("ui.cb_credited_instruments", "As credited instrument names"))
        self.ui.cb_credited_vocals.setText(self.api.tr("cb_credited_vocals", "As credited vocal names"))
        self.ui.label_22.setText(self.api.tr("ui.include_performer_attributes", "Include Performance Attributes"))
        self.ui.label_2.setText(
            self.api.tr(
                "ui.include_performer_attributes_description",
                (
                    "<html><head/><body><p>This option determines whether or not performance attributes that have been "
                    "specified in the performance relationship are included in the output. Note that the display of the "
                    "attributes can be enabled or disabled separately for instruments and vocals.</p></body></html>"
                )
            )
        )
        self.ui.cb_guest_vocals.setText(self.api.tr("ui.cb_guest_vocals", "Vocals"))
        self.ui.cb_solo_instruments.setText(self.api.tr("ui.cb_solo_instruments", "Instruments"))
        self.ui.cb_guest_instruments.setText(self.api.tr("ui.cb_guest_instruments", "Instruments"))
        self.ui.label_7.setText(self.api.tr("ui.guest", "Guest:"))
        self.ui.cb_additional_instruments.setText(self.api.tr("ui.cb_additional_instruments", "Instruments"))
        self.ui.cb_solo_vocals.setText(self.api.tr("ui.cb_solo_vocals", "Vocals"))
        self.ui.cb_additional_vocals.setText(self.api.tr("ui.cb_additional_vocals", "Vocals"))
        self.ui.label_8.setText(self.api.tr("ui.solo", "Solo:"))
        self.ui.label_6.setText(self.api.tr("ui.additional", "Additional:"))
        self.ui.cb_vocal_types.setText(self.api.tr("ui.cb_vocal_types", "Vocals"))
        self.ui.label_13.setText(self.api.tr("ui.vocal_types", "Vocal Types:"))
        self.ui.label_23.setText(self.api.tr("ui.grouping", "Grouping"))
        self.ui.label_14.setText(
            self.api.tr(
                "ui.grouping_description",
                "<html><head/><body><p>This determines how the items in the variable are grouped.</p></body></html>"
            )
        )
        self.ui.label_15.setText(self.api.tr("ui.group_by", "Group by:"))
        self.ui.rb_group_artist.setText(self.api.tr("ui.rb_group_artist", "Artist"))
        self.ui.rb_group_instrument.setText(self.api.tr("ui.rb_group_instrument", "Instrument / Vocal"))
        self.ui.label_24.setText(self.api.tr("ui.keyword_sections", "Keyword Sections Assignment"))
        self.ui.format_description_2.setText(
            self.api.tr(
                "ui.keyword_sections_description",
                (
                    "<html><head/><body><p>These settings determine the format for the items in the variable. The format is "
                    "divided into six parts: the artist; the instrument or vocal; and four user selectable sections for the "
                    "extra information. This is set out as:</p><p>With Artist grouping:</p><p align=\"center\">Artist: <span "
                    "style=\"font-weight:600;\">[Section 1]</span>Instrument/Vocal<span style=\"font-weight:600;\">[Section 2]"
                    "[Section 3][Section 4]</span></p><p>With Instrument/Vocal grouping:</p><p align=\"center\"><span style=\""
                    "font-weight:600;\">[Section 1]</span>Instrument/Vocal<span style=\"font-weight:600;\">[Section 2][Section "
                    "3]</span>: Artist<span style=\" font-weight:600;\">[Section 4]</span></p><p>You can select the section in "
                    "which each of the extra information words appear.</p></body></html>"
                )
            )
        )
        self.ui.additional_rb_1.setText(self.api.tr("ui.additional_rb_1", "1"))
        self.ui.additional_rb_2.setText(self.api.tr("ui.additional_rb_2", "2"))
        self.ui.additional_rb_3.setText(self.api.tr("ui.additional_rb_3", "3"))
        self.ui.additional_rb_4.setText(self.api.tr("ui.additional_rb_4", "4"))
        self.ui.guest_rb_1.setText(self.api.tr("ui.guest_rb_1", "1"))
        self.ui.guest_rb_2.setText(self.api.tr("ui.guest_rb_2", "2"))
        self.ui.guest_rb_3.setText(self.api.tr("ui.guest_rb_3", "3"))
        self.ui.guest_rb_4.setText(self.api.tr("ui.guest_rb_4", "4"))
        self.ui.solo_rb_1.setText(self.api.tr("ui.solo_rb_1", "1"))
        self.ui.solo_rb_2.setText(self.api.tr("ui.solo_rb_2", "2"))
        self.ui.solo_rb_3.setText(self.api.tr("ui.solo_rb_3", "3"))
        self.ui.solo_rb_4.setText(self.api.tr("ui.solo_rb_4", "4"))
        self.ui.label_16.setText(self.api.tr("ui.label_additional", "Additional:"))
        self.ui.label_17.setText(self.api.tr("ui.label_guest", "Guest:"))
        self.ui.label_18.setText(self.api.tr("ui.label_solo", "Solo:"))
        self.ui.label_19.setText(self.api.tr("ui.label_vocal_types", "Vocal Types:"))
        self.ui.vocals_rb_1.setText(self.api.tr("ui.vocals_rb_1", "1"))
        self.ui.vocals_rb_2.setText(self.api.tr("ui.vocals_rb_2", "2"))
        self.ui.vocals_rb_3.setText(self.api.tr("ui.vocals_rb_3", "3"))
        self.ui.vocals_rb_4.setText(self.api.tr("ui.vocals_rb_4", "4"))
        self.ui.label_25.setText(self.api.tr("ui.label_section_display_settings", "Section Display Settings"))
        self.ui.label_27.setText(
            self.api.tr(
                "ui.label_section_display_settings_description",
                (
                    "<html><head/><body><p>For each of the sections you can select the starting characters, "
                    "the characters separating entries, and the ending characters. Note that leading or trailing "
                    "spaces must be included in the settings and will not be automatically added. If no separator "
                    "characters are entered, the items within a section will be automatically separated by a single "
                    "space.</p></body></html>"
                )
            )
        )
        self.ui.format_group_2_sep_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.format_group_2_start_char.setText(self.api.tr("ui.format_group_2_start_char", ", "))
        self.ui.format_group_2_start_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.format_group_4_end_char.setText(self.api.tr("ui.format_group_4_end_char", ")"))
        self.ui.format_group_4_end_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.format_group_4_start_char.setText(self.api.tr("ui.format_group_4_start_char", " ("))
        self.ui.format_group_4_start_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.label_9.setText(self.api.tr("ui.label_section_4", "Section 4"))
        self.ui.label_12.setText(self.api.tr("ui.label_end_chars", "End Chars"))
        self.ui.label_5.setText(self.api.tr("ui.label_section_1", "Section 1"))
        self.ui.label_3.setText(self.api.tr("ui.label_section_2", "Section 2"))
        self.ui.format_group_3_sep_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.format_group_4_sep_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.format_group_1_start_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.label_4.setText(self.api.tr("ui.label_section_3", "Section 3"))
        self.ui.label_11.setText(self.api.tr("ui.label_sep_chars", "Sep Chars"))
        self.ui.format_group_3_start_char.setText(self.api.tr("ui.format_group_3_start_char", " ("))
        self.ui.format_group_3_start_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.format_group_1_end_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.format_group_2_end_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.format_group_3_end_char.setText(self.api.tr("ui.format_group_3_end_char", ")"))
        self.ui.format_group_3_end_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.format_group_1_sep_char.setPlaceholderText(self.api.tr("ui.placeholder_blank", "(blank)"))
        self.ui.label_10.setText(self.api.tr("ui.label_start_chars", "Start Chars"))
        self.ui.label_26.setText(self.api.tr("ui.label_example_output", "Example Output"))

        # Enable external link
        self.ui.format_description.setOpenExternalLinks(True)

        # Local settings to use for examples
        self.settings = PluginOptions(self.api)
        self.settings.load_from_config()

        self.processor = CombinePerformerTags(ExampleMetadata.RELS, api=self.api)

        self.ui.cb_credited_artists.clicked.connect(self._update_settings_and_examples)
        self.ui.cb_credited_instruments.clicked.connect(self._update_settings_and_examples)
        self.ui.cb_credited_vocals.clicked.connect(self._update_settings_and_examples)

        self.ui.cb_additional_instruments.clicked.connect(self._update_settings_and_examples)
        self.ui.cb_guest_instruments.clicked.connect(self._update_settings_and_examples)
        self.ui.cb_solo_instruments.clicked.connect(self._update_settings_and_examples)

        self.ui.cb_additional_vocals.clicked.connect(self._update_settings_and_examples)
        self.ui.cb_guest_vocals.clicked.connect(self._update_settings_and_examples)
        self.ui.cb_solo_vocals.clicked.connect(self._update_settings_and_examples)

        self.ui.cb_vocal_types.clicked.connect(self._update_settings_and_examples)

        self.ui.rb_group_artist.clicked.connect(self._update_settings_and_examples)
        self.ui.rb_group_instrument.clicked.connect(self._update_settings_and_examples)

        self.ui.additional_rb_1.clicked.connect(self._update_settings_and_examples)
        self.ui.additional_rb_2.clicked.connect(self._update_settings_and_examples)
        self.ui.additional_rb_3.clicked.connect(self._update_settings_and_examples)
        self.ui.additional_rb_4.clicked.connect(self._update_settings_and_examples)

        self.ui.guest_rb_1.clicked.connect(self._update_settings_and_examples)
        self.ui.guest_rb_2.clicked.connect(self._update_settings_and_examples)
        self.ui.guest_rb_3.clicked.connect(self._update_settings_and_examples)
        self.ui.guest_rb_4.clicked.connect(self._update_settings_and_examples)

        self.ui.solo_rb_1.clicked.connect(self._update_settings_and_examples)
        self.ui.solo_rb_2.clicked.connect(self._update_settings_and_examples)
        self.ui.solo_rb_3.clicked.connect(self._update_settings_and_examples)
        self.ui.solo_rb_4.clicked.connect(self._update_settings_and_examples)

        self.ui.vocals_rb_1.clicked.connect(self._update_settings_and_examples)
        self.ui.vocals_rb_2.clicked.connect(self._update_settings_and_examples)
        self.ui.vocals_rb_3.clicked.connect(self._update_settings_and_examples)
        self.ui.vocals_rb_4.clicked.connect(self._update_settings_and_examples)

        self.ui.format_group_1_start_char.editingFinished.connect(self._update_settings_and_examples)
        self.ui.format_group_2_start_char.editingFinished.connect(self._update_settings_and_examples)
        self.ui.format_group_3_start_char.editingFinished.connect(self._update_settings_and_examples)
        self.ui.format_group_4_start_char.editingFinished.connect(self._update_settings_and_examples)

        self.ui.format_group_1_sep_char.editingFinished.connect(self._update_settings_and_examples)
        self.ui.format_group_2_sep_char.editingFinished.connect(self._update_settings_and_examples)
        self.ui.format_group_3_sep_char.editingFinished.connect(self._update_settings_and_examples)
        self.ui.format_group_4_sep_char.editingFinished.connect(self._update_settings_and_examples)

        self.ui.format_group_1_end_char.editingFinished.connect(self._update_settings_and_examples)
        self.ui.format_group_2_end_char.editingFinished.connect(self._update_settings_and_examples)
        self.ui.format_group_3_end_char.editingFinished.connect(self._update_settings_and_examples)
        self.ui.format_group_4_end_char.editingFinished.connect(self._update_settings_and_examples)

    def _log_widget_error(self, error: Exception, widget: str) -> None:
        self.api.logger.error(f"{error}: Unable to find widget '{widget}'.")

    def load(self) -> None:
        """Load the option settings.
        """
        self.ui.cb_credited_artists.setChecked(self.api.plugin_config[self.keys.OPT_CREDITED_ARTIST])
        self.ui.cb_credited_instruments.setChecked(self.api.plugin_config[self.keys.OPT_CREDITED_INSTRUMENT])
        self.ui.cb_credited_vocals.setChecked(self.api.plugin_config[self.keys.OPT_CREDITED_VOCAL])
        self.ui.cb_additional_instruments.setChecked(self.api.plugin_config[self.keys.OPT_INSTRUMENT_ATTR_ADDITIONAL])
        self.ui.cb_guest_instruments.setChecked(self.api.plugin_config[self.keys.OPT_INSTRUMENT_ATTR_GUEST])
        self.ui.cb_solo_instruments.setChecked(self.api.plugin_config[self.keys.OPT_INSTRUMENT_ATTR_SOLO])
        self.ui.cb_additional_vocals.setChecked(self.api.plugin_config[self.keys.OPT_VOCAL_ATTR_ADDITIONAL])
        self.ui.cb_guest_vocals.setChecked(self.api.plugin_config[self.keys.OPT_VOCAL_ATTR_GUEST])
        self.ui.cb_solo_vocals.setChecked(self.api.plugin_config[self.keys.OPT_VOCAL_ATTR_SOLO])
        self.ui.cb_vocal_types.setChecked(self.api.plugin_config[self.keys.OPT_VOCAL_ATTR_TYPES])

        if self.api.plugin_config[self.keys.OPT_TAG_GROUP_BY_ARTIST]:
            self.ui.rb_group_artist.setChecked(True)
        else:
            self.ui.rb_group_instrument.setChecked(True)

        def _set_rb(radio_button: str, number: int) -> None:
            """Set the appropriate radio button as selected.

            Args:
                radio_button (str): Prefix of radio button widget.
                number (int): Button number to set as selected.
            """
            try:
                widget = f"{radio_button}_{number}"
                self.ui.scrollArea.findChild(QtWidgets.QRadioButton, widget).setChecked(True)
            except (KeyError, AttributeError) as e:
                self._log_widget_error(e, widget)

        # Settings for keywords
        _set_rb('additional_rb', self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_ADDITIONAL])
        _set_rb('guest_rb', self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_GUEST])
        _set_rb('solo_rb', self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_SOLO])
        _set_rb('vocals_rb', self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_VOCALS])

        # Settings for word group 1
        self.ui.format_group_1_start_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_1_START])
        self.ui.format_group_1_end_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_1_END])
        self.ui.format_group_1_sep_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_1_SEP])

        # Settings for word group 2
        self.ui.format_group_2_start_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_2_START])
        self.ui.format_group_2_end_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_2_END])
        self.ui.format_group_2_sep_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_2_SEP])

        # Settings for word group 3
        self.ui.format_group_3_start_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_3_START])
        self.ui.format_group_3_end_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_3_END])
        self.ui.format_group_3_sep_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_3_SEP])

        # Settings for word group 4
        self.ui.format_group_4_start_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_4_START])
        self.ui.format_group_4_end_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_4_END])
        self.ui.format_group_4_sep_char.setText(self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_4_SEP])

        self.update_examples()

    def _get_rb(self, radio_button: str, max_number: int) -> int:
        """Gets the number of the radio button set as selected.

        Args:
            radio_button (str): Prefix of radio button widgets to check.
            max_number (int): Maximum number of radio button widgets to check.

        Returns:
            int: Number of the radio button marked as selected.  Defaults to 1.
        """
        for i in range(1, max_number + 1):
            try:
                widget = f"{radio_button}_{i}"
                if self.ui.scrollArea.findChild(QtWidgets.QRadioButton, widget).isChecked():
                    return i
            except (KeyError, AttributeError) as e:
                self._log_widget_error(e, widget)
        return 1

    def save(self) -> None:
        """Save the option settings.
        """
        self.api.plugin_config[self.keys.OPT_CREDITED_ARTIST] = self.ui.cb_credited_artists.isChecked()
        self.api.plugin_config[self.keys.OPT_CREDITED_INSTRUMENT] = self.ui.cb_credited_instruments.isChecked()
        self.api.plugin_config[self.keys.OPT_CREDITED_VOCAL] = self.ui.cb_credited_vocals.isChecked()
        self.api.plugin_config[self.keys.OPT_INSTRUMENT_ATTR_ADDITIONAL] = self.ui.cb_additional_instruments.isChecked()
        self.api.plugin_config[self.keys.OPT_INSTRUMENT_ATTR_GUEST] = self.ui.cb_guest_instruments.isChecked()
        self.api.plugin_config[self.keys.OPT_INSTRUMENT_ATTR_SOLO] = self.ui.cb_solo_instruments.isChecked()
        self.api.plugin_config[self.keys.OPT_VOCAL_ATTR_ADDITIONAL] = self.ui.cb_additional_vocals.isChecked()
        self.api.plugin_config[self.keys.OPT_VOCAL_ATTR_GUEST] = self.ui.cb_guest_vocals.isChecked()
        self.api.plugin_config[self.keys.OPT_VOCAL_ATTR_SOLO] = self.ui.cb_solo_vocals.isChecked()
        self.api.plugin_config[self.keys.OPT_VOCAL_ATTR_TYPES] = self.ui.cb_vocal_types.isChecked()
        self.api.plugin_config[self.keys.OPT_TAG_GROUP_BY_ARTIST] = self.ui.rb_group_artist.isChecked()

        # Settings for word group 1
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_1_START] = self.ui.format_group_1_start_char.text()
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_1_END] = self.ui.format_group_1_end_char.text()
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_1_SEP] = self.ui.format_group_1_sep_char.text()

        # Settings for word group 2
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_2_START] = self.ui.format_group_2_start_char.text()
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_2_END] = self.ui.format_group_2_end_char.text()
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_2_SEP] = self.ui.format_group_2_sep_char.text()

        # Settings for word group 3
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_3_START] = self.ui.format_group_3_start_char.text()
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_3_END] = self.ui.format_group_3_end_char.text()
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_3_SEP] = self.ui.format_group_3_sep_char.text()

        # Settings for word group 4
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_4_START] = self.ui.format_group_4_start_char.text()
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_4_END] = self.ui.format_group_4_end_char.text()
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_4_SEP] = self.ui.format_group_4_sep_char.text()

        # Settings for keywords
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_ADDITIONAL] = self._get_rb('additional_rb', 4)
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_GUEST] = self._get_rb('guest_rb', 4)
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_SOLO] = self._get_rb('solo_rb', 4)
        self.api.plugin_config[self.keys.OPT_FORMAT_GROUP_VOCALS] = self._get_rb('vocals_rb', 4)

    def save_to_example_settings(self) -> None:
        """Save the option settings used for the examples.
        """
        self.settings.OPT_CREDITED_ARTIST = self.ui.cb_credited_artists.isChecked()
        self.settings.OPT_CREDITED_INSTRUMENT = self.ui.cb_credited_instruments.isChecked()
        self.settings.OPT_CREDITED_VOCAL = self.ui.cb_credited_vocals.isChecked()
        self.settings.OPT_INSTRUMENT_ATTR_ADDITIONAL = self.ui.cb_additional_instruments.isChecked()
        self.settings.OPT_INSTRUMENT_ATTR_GUEST = self.ui.cb_guest_instruments.isChecked()
        self.settings.OPT_INSTRUMENT_ATTR_SOLO = self.ui.cb_solo_instruments.isChecked()
        self.settings.OPT_VOCAL_ATTR_ADDITIONAL = self.ui.cb_additional_vocals.isChecked()
        self.settings.OPT_VOCAL_ATTR_GUEST = self.ui.cb_guest_vocals.isChecked()
        self.settings.OPT_VOCAL_ATTR_SOLO = self.ui.cb_solo_vocals.isChecked()
        self.settings.OPT_VOCAL_ATTR_TYPES = self.ui.cb_vocal_types.isChecked()
        self.settings.OPT_TAG_GROUP_BY_ARTIST = self.ui.rb_group_artist.isChecked()

        # Settings for word group 1
        self.settings.OPT_FORMAT_GROUP_1_START = self.ui.format_group_1_start_char.text()
        self.settings.OPT_FORMAT_GROUP_1_END = self.ui.format_group_1_end_char.text()
        self.settings.OPT_FORMAT_GROUP_1_SEP = self.ui.format_group_1_sep_char.text()

        # Settings for word group 2
        self.settings.OPT_FORMAT_GROUP_2_START = self.ui.format_group_2_start_char.text()
        self.settings.OPT_FORMAT_GROUP_2_END = self.ui.format_group_2_end_char.text()
        self.settings.OPT_FORMAT_GROUP_2_SEP = self.ui.format_group_2_sep_char.text()

        # Settings for word group 3
        self.settings.OPT_FORMAT_GROUP_3_START = self.ui.format_group_3_start_char.text()
        self.settings.OPT_FORMAT_GROUP_3_END = self.ui.format_group_3_end_char.text()
        self.settings.OPT_FORMAT_GROUP_3_SEP = self.ui.format_group_3_sep_char.text()

        # Settings for word group 4
        self.settings.OPT_FORMAT_GROUP_4_START = self.ui.format_group_4_start_char.text()
        self.settings.OPT_FORMAT_GROUP_4_END = self.ui.format_group_4_end_char.text()
        self.settings.OPT_FORMAT_GROUP_4_SEP = self.ui.format_group_4_sep_char.text()

        # Settings for keywords
        self.settings.OPT_FORMAT_GROUP_ADDITIONAL = self._get_rb('additional_rb', 4)
        self.settings.OPT_FORMAT_GROUP_GUEST = self._get_rb('guest_rb', 4)
        self.settings.OPT_FORMAT_GROUP_SOLO = self._get_rb('solo_rb', 4)
        self.settings.OPT_FORMAT_GROUP_VOCALS = self._get_rb('vocals_rb', 4)

    def _update_settings_and_examples(self) -> None:
        self.save_to_example_settings()
        self.processor.settings = self.settings
        self.update_examples()

    def update_examples(self) -> None:
        """Update the examples displayed.
        """
        items = self.processor.get_performers()
        self.ui.example_items.setText('\n'.join(items))


class ExampleMetadata():
    """Metadata to use for the examples display.
    """
    # pylint: disable=too-few-public-methods

    RELS = [
        {
            'artist': {
                'disambiguation': 'American singer-songwriter',
                'id': '88527d26-7496-47c5-8358-ebdb1868a90f',
                'name': 'Jackson Browne',
                'sort-name': 'Browne, Jackson',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {},
            'attribute-ids': {'acoustic guitar': '00beaf8e-a781-431c-8130-7c2871696b7d'},
            'attribute-values': {},
            'attributes': ['acoustic guitar'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': '',
            'target-type': 'artist',
            'type': 'instrument',
            'type-id': '59054b12-01ac-43ee-a618-285fd397e461'
        },

        {
            'artist': {
                'disambiguation': 'American singer-songwriter',
                'id': '88527d26-7496-47c5-8358-ebdb1868a90f',
                'name': 'Jackson Browne',
                'sort-name': 'Browne, Jackson',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {},
            'attribute-ids': {'piano': 'b3eac5f9-7859-4416-ac39-7154e2e8d348'},
            'attribute-values': {},
            'attributes': ['piano'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': '',
            'target-type': 'artist',
            'type': 'instrument',
            'type-id': '59054b12-01ac-43ee-a618-285fd397e461'
        },

        {
            'artist': {
                'disambiguation': 'US-based Canadian violinist, composer, conductor and arranger',
                'id': 'c4fe833e-0f24-42ad-ae2b-b9d088c282b4',
                'name': 'David Campbell',
                'sort-name': 'Campbell, David',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {},
            'attribute-ids': {'viola': '377e007a-33fe-4825-9bef-136cf5cf581a'},
            'attribute-values': {},
            'attributes': ['viola'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': '',
            'target-type': 'artist',
            'type': 'instrument',
            'type-id': '59054b12-01ac-43ee-a618-285fd397e461'
        },

        {
            'artist': {
                'disambiguation': '',
                'id': 'ea0fc609-3b92-434d-adca-858f10f9c767',
                'name': 'Jimmie Fadden',
                'sort-name': 'Fadden, Jimmie',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {'harmonica': 'mouth harp'},
            'attribute-ids': {'harmonica': '63e37f1a-30b6-4746-8a49-dfb55be3cdd1'},
            'attribute-values': {},
            'attributes': ['harmonica', 'solo'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': 'Jim Fadden',
            'target-type': 'artist',
            'type': 'instrument',
            'type-id': '59054b12-01ac-43ee-a618-285fd397e461'
        },

        {
            'artist': {
                'disambiguation': 'US drummer with Derek and the Dominos',
                'id': 'f5ee63be-2ffa-479e-afb9-a89201c3b1f0',
                'name': 'Jim Gordon',
                'sort-name': 'Gordon, Jim',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {},
            'attribute-ids': {'organ': '55a37f4f-39a4-45a7-851d-586569985519'},
            'attribute-values': {},
            'attributes': ['organ'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': '',
            'target-type': 'artist',
            'type': 'instrument',
            'type-id': '59054b12-01ac-43ee-a618-285fd397e461'
        },

        {
            'artist': {
                'disambiguation': '',
                'id': 'f7b1e334-2aaa-4ef2-85f9-5c2c8cdb90dc',
                'name': 'Sneaky Pete Kleinow',
                'sort-name': 'Kleinow, Sneaky Pete',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {},
            'attribute-ids': {'pedal steel guitar': '4a10b219-65ac-4b6c-950d-acc8461266c7'},
            'attribute-values': {},
            'attributes': ['pedal steel guitar'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': 'Sneaky Pete',
            'target-type': 'artist',
            'type': 'instrument',
            'type-id': '59054b12-01ac-43ee-a618-285fd397e461'
        },

        {
            'artist': {
                'disambiguation': '',
                'id': '6a002755-c0e3-4530-b608-eb10bb994c01',
                'name': 'Russ Kunkel',
                'sort-name': 'Kunkel, Russ',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {},
            'attribute-ids': {'drums (drum set)': '12092505-6ee1-46af-a15a-b5b468b6b155'},
            'attribute-values': {},
            'attributes': ['drums (drum set)'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': '',
            'target-type': 'artist',
            'type': 'instrument',
            'type-id': '59054b12-01ac-43ee-a618-285fd397e461'
        },

        {
            'artist': {
                'disambiguation': 'bassist, session musician',
                'id': '9c840b50-e89f-4eb4-8aac-695fdbbfc8a2',
                'name': 'Leland Sklar',
                'sort-name': 'Sklar, Leland',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {},
            'attribute-ids': {'bass': '6505f98c-f698-4406-8bf4-8ca43d05c36f'},
            'attribute-values': {},
            'attributes': ['bass'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': '',
            'target-type': 'artist',
            'type': 'instrument',
            'type-id': '59054b12-01ac-43ee-a618-285fd397e461'
        },

        {
            'artist': {
                'disambiguation': 'US bluegrass and country-rock guitarist',
                'id': '88970b96-d093-4ab8-b194-c91479b4387e',
                'name': 'Clarence White',
                'sort-name': 'White, Clarence',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {},
            'attribute-ids': {'acoustic guitar': '00beaf8e-a781-431c-8130-7c2871696b7d'},
            'attribute-values': {},
            'attributes': ['acoustic guitar', 'additional'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': '',
            'target-type': 'artist',
            'type': 'instrument',
            'type-id': '59054b12-01ac-43ee-a618-285fd397e461'
        },

        {
            'artist': {
                'disambiguation': 'American singer-songwriter',
                'id': '88527d26-7496-47c5-8358-ebdb1868a90f',
                'name': 'Jackson Browne',
                'sort-name': 'Browne, Jackson',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {},
            'attribute-ids': {'lead vocals': '8e2a3255-87c2-4809-a174-98cb3704f1a5'},
            'attribute-values': {},
            'attributes': ['lead vocals'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': '',
            'target-type': 'artist',
            'type': 'vocal',
            'type-id': '0fdbe3c6-7700-4a31-ae54-b53f06ae1cfa'
        },

        {
            'artist': {
                'disambiguation': '',
                'id': 'e90f9815-221d-4e10-8675-e75c07988113',
                'name': 'David Crosby',
                'sort-name': 'Crosby, David',
                'type': 'Person',
                'type-id': 'b6e035f4-3ce9-331c-97df-83397230b0df'
            },
            'attribute-credits': {'other vocals': 'harmony vocals'},
            'attribute-ids': {'other vocals': 'c359be96-620a-435c-bd25-2eb0ce81a22e'},
            'attribute-values': {},
            'attributes': ['other vocals', 'guest'],
            'begin': None,
            'direction': 'backward',
            'end': None,
            'ended': False,
            'source-credit': '',
            'target-credit': '',
            'target-type': 'artist',
            'type': 'vocal',
            'type-id': '0fdbe3c6-7700-4a31-ae54-b53f06ae1cfa'
        },
    ]


def enable(api: PluginApi) -> None:
    """Called when plugin is enabled."""
    keys = PluginOptions()  # Get unintialized list to provide Picard option settings keys

    # Register option settings
    api.plugin_config.register_option(keys.OPT_CREDITED_ARTIST, True)
    api.plugin_config.register_option(keys.OPT_CREDITED_INSTRUMENT, True)
    api.plugin_config.register_option(keys.OPT_CREDITED_VOCAL, True)
    api.plugin_config.register_option(keys.OPT_INSTRUMENT_ATTR_ADDITIONAL, True)
    api.plugin_config.register_option(keys.OPT_INSTRUMENT_ATTR_GUEST, True)
    api.plugin_config.register_option(keys.OPT_INSTRUMENT_ATTR_SOLO, True)
    api.plugin_config.register_option(keys.OPT_VOCAL_ATTR_ADDITIONAL, True)
    api.plugin_config.register_option(keys.OPT_VOCAL_ATTR_GUEST, True)
    api.plugin_config.register_option(keys.OPT_VOCAL_ATTR_SOLO, True)
    api.plugin_config.register_option(keys.OPT_VOCAL_ATTR_TYPES, True)

    api.plugin_config.register_option(keys.OPT_TAG_GROUP_BY_ARTIST, True)

    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_ADDITIONAL, 3)
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_GUEST, 4)
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_SOLO, 3)
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_VOCALS, 2)
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_1_START, '')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_1_END, ' ')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_1_SEP, '')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_2_START, ', ')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_2_END, '')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_2_SEP, '')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_3_START, ' (')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_3_END, ')')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_3_SEP, '')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_4_START, ' (')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_4_END, ')')
    api.plugin_config.register_option(keys.OPT_FORMAT_GROUP_4_SEP, '')

    # Migrate settings from 2.x version if available
    migrate_settings(api)

    # Register script variable
    api.register_script_variable(
        name="_performers",
        documentation=api.tr(
            "variable.performers",
            (
                "All instrument and vocal performer tags combined into a multi-value variable, with the format based "
                'on the settings page under "Options..." > "Plugins".'
            )
        )
    )

    # Register processor
    api.register_track_metadata_processor(combine_performer_tags)

    # Register options page
    api.register_options_page(CombinePerformerTagsOptionsPage)


def migrate_settings(api: PluginApi):
    cfg = get_config()
    if cfg.setting.raw_value("cpt_cred_artist") is None:
        return

    api.logger.info("Migrating settings from 2.x version.")

    keys = PluginOptions()  # Get unintialized list to provide Picard option settings keys
    mapping = [
        ('cpt_cred_artist', keys.OPT_CREDITED_ARTIST, bool),
        ('cpt_cred_instrument', keys.OPT_CREDITED_INSTRUMENT, bool),
        ('cpt_cred_vocal', keys.OPT_CREDITED_VOCAL, bool),
        ('cpt_inst_attr_additional', keys.OPT_INSTRUMENT_ATTR_ADDITIONAL, bool),
        ('cpt_inst_attr_guest', keys.OPT_INSTRUMENT_ATTR_GUEST, bool),
        ('cpt_inst_attr_solo', keys.OPT_INSTRUMENT_ATTR_SOLO, bool),
        ('cpt_vocal_attr_additional', keys.OPT_VOCAL_ATTR_ADDITIONAL, bool),
        ('cpt_vocal_attr_guest', keys.OPT_VOCAL_ATTR_GUEST, bool),
        ('cpt_vocal_attr_solo', keys.OPT_VOCAL_ATTR_SOLO, bool),
        ('cpt_vocal_attr_types', keys.OPT_VOCAL_ATTR_TYPES, bool),
        ('cpt_group_by_artist', keys.OPT_TAG_GROUP_BY_ARTIST, bool),
        ('cpt_format_group_additional', keys.OPT_FORMAT_GROUP_ADDITIONAL, int),
        ('cpt_format_group_guest', keys.OPT_FORMAT_GROUP_GUEST, int),
        ('cpt_format_group_solo', keys.OPT_FORMAT_GROUP_SOLO, int),
        ('cpt_format_group_vocals', keys.OPT_FORMAT_GROUP_VOCALS, int),
        ('cpt_format_group_1_start_char', keys.OPT_FORMAT_GROUP_1_START, str),
        ('cpt_format_group_1_end_char', keys.OPT_FORMAT_GROUP_1_END, str),
        ('cpt_format_group_1_sep_char', keys.OPT_FORMAT_GROUP_1_SEP, str),
        ('cpt_format_group_2_start_char', keys.OPT_FORMAT_GROUP_2_START, str),
        ('cpt_format_group_2_end_char', keys.OPT_FORMAT_GROUP_2_END, str),
        ('cpt_format_group_2_sep_char', keys.OPT_FORMAT_GROUP_2_SEP, str),
        ('cpt_format_group_3_start_char', keys.OPT_FORMAT_GROUP_3_START, str),
        ('cpt_format_group_3_end_char', keys.OPT_FORMAT_GROUP_3_END, str),
        ('cpt_format_group_3_sep_char', keys.OPT_FORMAT_GROUP_3_SEP, str),
        ('cpt_format_group_4_start_char', keys.OPT_FORMAT_GROUP_4_START, str),
        ('cpt_format_group_4_end_char', keys.OPT_FORMAT_GROUP_4_END, str),
        ('cpt_format_group_4_sep_char', keys.OPT_FORMAT_GROUP_4_SEP, str),
    ]

    for old_key, new_key, qtype in mapping:
        if cfg.setting.raw_value(old_key) is None:
            api.logger.debug("No old setting for key: '%s'", old_key,)
            continue
        api.plugin_config[new_key] = cfg.setting.raw_value(old_key, qtype=qtype)
        cfg.setting.remove(old_key)
