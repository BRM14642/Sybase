import xml.etree.ElementTree as ET

class XML_Handler:

    def __init__(self):
        self.path = 'src/scripts/templates/packaging-build.xml'
        self.jar_mapping = self.parse_packaging_build(self.path)

    def parse_packaging_build(self, path):
        tree = ET.parse(path)
        root = tree.getroot()
        jar_mapping = {}

        for target in root.findall('target'):
            jar_name = target.get('description')
            if jar_name:
                for zipfileset in target.findall('jar/zipfileset'):
                    includes = zipfileset.get('includes')
                    if includes:
                        paths = includes.split(',')
                        for path in paths:
                            path = path.strip().split('/*.')[0] + '/'
                            if path == '/':
                                continue
                            jar_mapping[path] = jar_name

        return jar_mapping

    def get_jar_for_class(self, class_path):
        for path, jar in self.jar_mapping.items():
            if path in class_path:
                return jar
        return None

    def class_belongs_to_jar(self, class_path):
        return any(path in class_path for path in self.jar_mapping)