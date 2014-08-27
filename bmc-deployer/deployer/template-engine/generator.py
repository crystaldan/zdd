"""
Load all the parameter from yaml file, and generate
    bmc.conf
    bmc.spec
    bmc-suf.xml


base class: generator

sub class:
    sufxmlfile
    inixmlfile
    specfile


"""
import yaml
import os
import pprint

from bdcutils import argparse

yamlstr1='''

- section:
  - name: install
  - parameters:
    - parameter: install_network
      mode: SA
      comment: |
        for 'parameter' specified the name of the parameter for the step.
        and it supports muiltible parameter, please use ',' to separate them.
      default: 192.168.1
      spec: string(min=6, max=11)

- section:
  - name: node
  - parameters:
    - parameter: mdf_cp1_mac
      mode: SA
      comment: |
        phase.
      default: 11:22:ss:cc:ff
      spec: mac()

    - parameter: mdf_cp2_mac
      mode: HA,SA
      comment:
      default: 11:22:ss:cc:ff
      spec: mac()

'''
class generator:

    def __init__(self, yamlobj, mode):
        self.mode = mode
        self.yamlobj = yamlobj
        self.inifilename = "/var/tmp/bmc.conf"
        self.specfilename = "/var/tmp/bmc.spec"
        self.sufxmlfilename = "/var/tmp/bmc-suf.xml"

    def check(self):
        if self.yamlobj == None:
            print("Yaml obj is None. Please check the yaml file.")
            return False
        if len(self.yamlobj) == 0:
            print("Yaml obj is empty. Please check the yaml file.")
            return False
        return True


    def ismodecorrect(self, modes):
        if modes == "" or modes == None:
            print("Mode is not valid.")
            return False

        if self.mode.upper() in modes.split(","):
            return True
        else:
            return False

    def generate(self):
        print("Generating...")
        return 0

class sufxmlfile(generator):

    def __init__(self, yamlobj, mode):
        generator.__init__(self, yamlobj, mode)

    def generate(self):

        CONF_TEMP_NAME = "bmc-configuration"

        if not self.check():
            print("Please check yaml file...")
            return False

        print("Start to generate template xml file for SUF...")

        # open the bmc.cf
        xmlfile = open(self.sufxmlfilename, "w")

        xmlfile.writelines('<configuration_template name="' + CONF_TEMP_NAME + '" description="' + CONF_TEMP_NAME + '">\n')

        # loop for the 'section' level.
        for section in yamlobj:

            # base on the section make the parameter into group.
            for element in section["section"]:

                # handle section name
                if element.keys()[0] == "name":
                    xmlfile.writelines('    <parameter_group name="' + element["name"] + '" description="' + element["name"] + '">\n')

                # handle the parameters.
                if element.keys()[0] == "parameters":
                    for parameter in element["parameters"]:

                        # check mode
                        if not self.ismodecorrect(parameter["mode"]):
                            continue
                        xmlfile.writelines('        <parameter name="' + parameter["parameter"] + '" description="' +
                            parameter["parameter"] + '" default="' + parameter["default"] + '"/>\n')

                xmlfile.writelines('    </parameter_group>\n')
                xmlfile.writelines("\n")

        xmlfile.writelines('</configuration_template>\n')
        xmlfile.close()

        print("Generate bmc-suf.xml successfully!")
        return True

class specfile(generator):

    def __init__(self, yamlobj, mode):
        generator.__init__(self, yamlobj, mode)

    def generate(self):

        if not self.check():
            print("Please check yaml file...")
            return False

        print("Start to generate spec file...")

        # open the bmc.cf
        specfile = open(self.specfilename, "w")

        for section in yamlobj:
            for element in section["section"]:

                # Handle the section name.
                if element.keys()[0] == "name":
                    specfile.writelines("[%s]\n" % element["name"])

                # handle the parameters issue.
                if element.keys()[0] == "parameters":
                    for parameter in element["parameters"]:

                        # check mode
                        if not self.ismodecorrect(parameter["mode"]):
                            continue

                        specfile.writelines("%s = %s\n"%(parameter["parameter"], parameter["spec"]))
                        specfile.writelines("\n")

        specfile.close()
        print("Generate bmc.spec successfully!")

        return True


class inifile(generator):

    def __init__(self, yamlobj, mode):
        generator.__init__(self, yamlobj, mode)

    def generate(self):

        if not self.check():
            print("Please check yaml file...")
            return False

        print("Start to generate ini file...")

        # lengh for the sperat line.
        linelen = 70

        # open the bmc.cf
        inifile = open(self.inifilename, "w")

        for section in yamlobj:
            for element in section["section"]:

                # Handle the section name.
                if element.keys()[0] == "name":
                    inifile.writelines("[%s]\n" % element["name"])

                # handle the parameters issue.
                if element.keys()[0] == "parameters":

                    for parameter in element["parameters"]:

                        # check mode
                        if not self.ismodecorrect(parameter["mode"]):
                            continue

                        if parameter["comment"] != None and parameter["comment"].rstrip().lstrip() != "":
                            inifile.writelines("#%s\n# " % (linelen * "-"))

                            # Replace the "\n" to the "\n#" for the comment.
                            inifile.writelines(parameter["comment"].replace("\n", "\n# ",
                                len((parameter["comment"].split("\n"))) - 2))
                            inifile.writelines("#%s\n" % (linelen * "-"))

                        inifile.writelines("%s = %s\n"%(parameter["parameter"], parameter["default"]))
                        inifile.writelines("\n")

        inifile.close()
        print("Generate bmc.cf successfully!")
        return 0

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='get the section, key and value')

    parser.add_argument('-m', '--mode', required=True, help='origin configuration file',  choices=['ha', 'sa', 'vm'])

    args = parser.parse_args()

    #yamlobj = yaml.load(yamlstr)
    yamlobj = yaml.load(yamlstr1)
    print str(yamlobj)

    mode = args.mode
    ini = inifile(yamlobj, mode)
    ini.generate()

    spec = specfile(yamlobj, mode)
    spec.generate()

    xml = sufxmlfile(yamlobj, mode)
    xml.generate()

