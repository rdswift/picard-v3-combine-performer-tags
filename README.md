# Combine Performer Tags

This plugin combines all instrument and vocal performer tags into a new multi-value variable `%_performers%` for each track. It requires that the "***Use track relationships***" setting is enabled in **Options** -> **Metadata**. Depending on the "Grouping" setting, each item in the variable is either the performer's name followed by the instruments and vocals they performed (e.g. "*Jackson Browne: acoustic guitar, piano, lead vocals*") or the instrument or vocal name followed by the artists associated with that instrument or vocal (e.g. "*acoustic guitar: Jackson Browne, Clarence White (additional)*").

The plugin makes no additional calls to the MusicBrainz database, and it does not remove any of the `%performer:*%` tags.

Please see the [User Guide](https://picard-plugins-user-guides.readthedocs.io/en/latest/combine_performer_tags/user_guide.html) for more information, including usage examples.

## Contributing

Please see the [Contribution Guidelines for MusicBrainz Picard Plugins](https://github.com/metabrainz/picard-plugins-registry/blob/main/PLUGIN_CONTRIBUTING.md) on how to help with development of this plugin.
