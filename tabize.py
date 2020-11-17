from lxml import etree
import sys
import numpy

parser = etree.XMLParser(ns_clean=True)
root = etree.parse(open(sys.argv[1]), parser).getroot()

acc = root.xpath("./protein_info")[0].get("id")
locs = []
scores = []
for entry in root.xpath("./global_feature[@id='localization']"):
  locs.append(entry.text.replace(" ", ""))
  scores.append(float(entry.get("score")))

print acc, ";".join(locs), ";".join(map(str, list(scores)))

