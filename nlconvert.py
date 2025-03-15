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
    if oldvalue.endswith("V"):
        oldvalue = oldvalue.split(" ")[0]
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

qpins = "ECB"
dipsize = 4
crystal3 = ["VCC","Q","GND"]

for part in ntlst.parts:
    partname = part.name
    if partname.startswith("SN74"):
        partname = partname[2:].replace("AN","")
    if partname == "C" or partname == "C_US" or partname == "C_Polarized" or partname == "C_Polarized_US":
        f.write("   CAP("+part.ref+", "+convertcap(part.value)+")\n")
    elif partname == "R" or partname == "R_US":
        f.write("   RES("+part.ref+", "+convertres(part.value)+")\n")
    elif partname.startswith("R_Network"):
        nwtype = int(partname[9:].replace("_US","").replace("_Split",""))
        for r in range(nwtype):
            f.write("   RES("+part.ref+"_"+str(r+1)+", "+convertres(part.value)+")\n")
        f.write("   NET_C(")
        first = True
        for r in range(nwtype):
            if first:
                first = False
            else:
                f.write(", ")
            f.write(part.ref+"_"+str(r+1)+".1")
        f.write(")\n")
    elif partname.startswith("R_Pack"):
        nwtype = int(partname[6:].replace("_Split","").replace("_US",""))
        for r in range(nwtype):
            f.write("   RES("+part.ref+"_"+str(r+1)+", "+convertres(part.value)+")\n")
    elif partname.startswith("SW_DIP"):
        dipsize = int(partname[8:])
        for r in range(dipsize):
            f.write("   SWITCH2("+part.ref+"_"+str(r+1)+")\n")
    elif partname == "R_Potentiometer" or partname == "R_Potentiometer_US":
        f.write("   POT("+part.ref+", "+convertres(part.value)+")\n")
    elif partname == "D":
        f.write("   DIODE("+part.ref+", \""+part.value+"\")\n")
    elif partname.startswith("Q"):
        qtype="NPN"
        if part.value.startswith("Q_PNP"):
            qtype = "PNP"
        qpins = partname[6:]
        f.write("   QBJT_EB("+part.ref+", \""+qtype+"\")\n")
    elif partname.startswith("Crystal"):
        f.write("   CLOCK("+part.ref+", \""+part.value.replace(",","")+"\")\n")
    elif partname == "74S287":
        f.write("   PROM_74S287_DIP("+part.ref+")\n")
        f.write("   PARAM("+part.ref+".ROM, \""+part.value+"\")\n")
    elif partname.startswith("74"):
        f.write("   TTL_")
        ttlno = partname.replace("LS","").replace("HC","").replace("AHC","")
        if ttlno == "7412":
            ttlno = "7410"
        if ttlno == "7409":
            ttlno = "7408"
        if ttlno == "74259":
            ttlno = "9334"
        f.write(ttlno)
        f.write("_DIP("+part.ref+")\n")
    elif partname == "MB7137":
        f.write("   EPROM_2716_DIP("+part.ref+")\n")
        f.write("   PARAM("+part.ref+".ROM, \""+part.value+"\")\n")
    elif partname.startswith("NE555"):
        f.write("   NE555_DIP("+part.ref+")\n")
    elif partname == "Am27LS00":
        f.write("   TTL_82S16_DIP("+part.ref+")\n")
    else:
        print(partname)

for net in ntlst.nets:
    netname = net.name.replace(" ","_").replace("~{","i").replace("}","").replace("(","").replace(")","").replace("&","and").replace(".","_").replace("/","b")
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
            
            if pin.ref.startswith("SW"):
                f.write(pin.ref+"_")
                pinno = int(pin.num)
                side = 1
                if (pinno > dipsize):
                    pinno = pinno % dipsize + 1
                    side = 2
                f.write(str(pinno)+"."+str(side))
            elif pin.ref.startswith("RN"):
                f.write(pin.ref+"_"+pin.num+".2")
            else:
                f.write(pin.ref+".")
                if pin.ref.startswith("Q"):
                    f.write(qpins[int(pin.num)-1])
                elif pin.ref.startswith("Y"):
                    f.write(crystal3[int(pin.num)-1])
                else:
                    f.write(pin.num)
        f.write(")\n")
f.write("}")
f.close()