import os
import markdown
import re
from datetime import datetime

# Metadata xml template
xmlTemplate = """<?xml version="1.0"?>
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier>{uid}</dc:identifier>
    <dc:type>{type}</dc:type>
    <dc:title>{title}</dc:title>
    <dc:subject>Artificial Intelligence for and by Teachers</dc:subject>
    <dc:description>{description}</dc:description>
    <dc:publisher>AI4T</dc:publisher>
    <dc:contributor>AI4T</dc:contributor>{contributor}
    <dc:date>{date}</dc:date>
    <dc:rights>cc by 4.0</dc:rights>
    <dc:language>{lang}</dc:language>
</metadata>
"""

# Walk recursively all files
basepath = u"./docs/1-Mooc/"
for path, dirs, files in os.walk(basepath):
    for file in files:
        file_no_ext, file_extension = os.path.splitext(file)
        file_no_lang, lang_extension = os.path.splitext(file_no_ext)
        # Cleanup old metadata
        if file_extension == '.xml' and lang_extension:
            os.remove(os.path.join(path, file))
for path, dirs, files in os.walk(basepath):
    for file in files:
        file_no_ext, file_extension = os.path.splitext(file)
        file_no_lang, lang_extension = os.path.splitext(file_no_ext)
        # Generate metadata for every markdown file
        if file_extension == '.md' and file_no_ext != "index":
            with open(os.path.join(path, file), 'r') as i:
                md = markdown.Markdown(extensions=['meta'])
                md.convert(i.read())
                # Extract uid from filename
                match_uid = re.search(
                    r"docs\/(.[^-]?)[^\/]*\/.*\/(\d)-(\d)-(\d)?([av])?.*",
                    os.path.join(path, file_no_ext)
                )
                if match_uid:
                    parsed_uid = dict(
                        part=match_uid.group(1),
                        module=match_uid.group(2),
                        sequence=match_uid.group(3),
                        unit=match_uid.group(4) if match_uid.group(4) else '0',
                        type=match_uid.group(5) if match_uid.group(5) else md.Meta.get('type', ['t'])[0].replace('"', '')[0]
                    )
                    uid = "EU.AI4T.O1.M{module}.{sequence}.{unit}{type}".format(**parsed_uid)
                else:
                    print(os.path.join(path, file_no_ext))
                    uid = "EU.AI4T.@todo"
                contributor = ""
                # Extract metadata from markdown
                if 'contributor' in md.Meta:
                    contributor += '\n    <dc:contributor>'
                    contributor += '</dc:contributor>\n    <dc:contributor>'.join(md.Meta['contributor'])
                    contributor += '</dc:contributor>'
                metadata = dict(
                    uid=uid,
                    type=md.Meta.get('type', ['text'])[0].replace('"', ''),
                    title=md.Meta.get('title', [''])[0].replace('"', ''),
                    description=md.Meta.get('description', [''])[0].replace('"', ''),
                    contributor=contributor,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    lang=lang_extension[1:]
                )
                # Write metadata file
                with open(os.path.join(path, file_no_ext+'.xml'), 'w+') as o:
                    o.write(xmlTemplate.format(**metadata))
