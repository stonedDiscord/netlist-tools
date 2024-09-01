from kinparse import *
import sys
import pathlib

inpath = pathlib.Path(sys.argv[1])
name = inpath.stem
ntlst = parse_netlist(inpath)

f = open("./nl_"+name+".cpp", "w")
f.write("#include \"netlist/devices/net_lib.h\"\n\n")
f.write("NETLIST_START("+name+")\n")
f.write("{\n")

# TODO replace 7412_ with 7410_
# TODO replace 7409_ with 7408_ 

def convertcap(oldvalue):
    oldvalue = oldvalue.upper().replace(",",".")
    if oldvalue.endswith("F"):
        oldvalue = oldvalue[:-1]
    if oldvalue.endswith("U"):
        return "CAP_U(" + oldvalue[:-1] + ")"
    elif oldvalue.endswith("N"):
        return "CAP_N(" + oldvalue[:-1] + ")"
    elif oldvalue.endswith("P"):
        return "CAP_P(" + oldvalue[:-1] + ")"
    return oldvalue

def convertres(oldvalue):
    oldvalue = oldvalue.upper().replace(",",".")
    if oldvalue.endswith("O") or oldvalue.endswith("Ω"):
        oldvalue = oldvalue[:-1]
    if oldvalue.endswith("K"):
        return "RES_K(" + oldvalue[:-1] + ")"
    elif oldvalue.endswith("M"):
        return "RES_M(" + oldvalue[:-1] + ")"
    return oldvalue

for part in ntlst.parts:
    if part.name == "C" or part.name == "C_US" or part.name == "C_Polarized" or part.name == "C_Polarized_US":
        f.write("   CAP("+part.ref+", "+convertcap(part.value)+")\n")
    elif part.name == "R" or part.name == "R_US":
        f.write("   RES("+part.ref+", "+convertres(part.value)+")\n")
    elif part.name.startswith("R_Network"):
        nwtype = int(part.name[9:].replace("_US","").replace("_Split",""))
        for r in range(nwtype):
            f.write("   RES("+part.ref+"_"+str(r)+", "+convertres(part.value)+")\n")
        f.write("   NET_C(")
        first = True
        for r in range(nwtype):
            if first:
                first = False
            else:
                f.write(", ")
            f.write(part.ref+"_"+str(r)+".1")
        f.write(")\n")
    elif part.name.startswith("R_Pack"):
        nwtype = int(part.name[6:].replace("_Split","").replace("_US",""))
        for r in range(nwtype):
            f.write("   RES("+part.ref+"_"+str(r)+", "+convertres(part.value)+")\n")
    elif part.name == "R_Potentiometer" or part.name == "R_Potentiometer_US":
        f.write("   POT("+part.ref+", "+convertres(part.value)+")\n")
    elif part.name == "D":
        f.write("   DIODE("+part.ref+", \""+part.value+"\")\n")
    elif part.name == "Q_NPN_ECB":
        qtype="NPN"
        if part.value.startswith("Q_PNP"):
            qtype = "PNP"
        f.write("   QBJT_EB("+part.ref+", \""+qtype+"\")\n")
    elif part.name == "74S287":
        f.write("   PROM_74S287_DIP("+part.ref+")\n")
        f.write("   PARAM("+part.ref+".ROM, \""+part.value+"\")\n")
    elif part.name.startswith("74"):
        f.write("   TTL_")
        ttlno = part.name.replace("LS","").replace("HC","").replace("AHC","")
        if ttlno == "7412":
            ttlno = "7410"
        if ttlno == "7409":
            ttlno = "7408"
        if ttlno == "74259":
            ttlno = "9334"
        f.write(ttlno)
        f.write("_DIP("+part.ref+")\n")
    elif part.name == "MB7137":
        f.write("   EPROM_2716_DIP("+part.ref+")\n")
        f.write("   PARAM("+part.ref+".ROM, \""+part.value+"\")\n")
    elif part.name == "NE555P":
        f.write("   NE555_DIP("+part.ref+")\n")
    else:
        print(part.name)

for net in ntlst.nets:
    netname = net.name.replace(" ","_").replace("~{","i").replace("}","").replace("(","").replace(")","").replace("&","AND").replace(".","_")
    if not ( netname.startswith("Net-") or netname.startswith("unconnected-")):
        f.write("   ALIAS(")
        f.write(netname)
        f.write(", ")
        f.write(net.pins[0].ref+"."+net.pins[0].num)
        f.write(")\n")
    if len(net.pins) > 1:
        f.write("   NET_C(")
        first = True
        for pin in net.pins:
            if first:
                first = False
            else:
                f.write(", ")
            f.write(pin.ref+"."+pin.num)
        f.write(")\n")
f.write("}")
f.close()