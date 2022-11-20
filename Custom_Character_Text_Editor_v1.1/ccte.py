# BotW: Custom Character Text Editor
# Last update: 14 Nov 2022

# Customizable edits to the Player and Keeper's (i.e., Link and Zelda's)
# name, gender, and pronouns.
# Use the output from this program with msyt-tools, then BCML to generate
# a working mod.

from argparse import RawDescriptionHelpFormatter
from prettytable import PrettyTable # user-friendlier option for displaying pronouns
from tqdm import tqdm # Required for showing progress bars

# built-in modules:
import math # needed for calculations when a character has 2 pronoun sets
import msvcrt as m  # Required for letting the user "Press any key to continue"
import os
import random # needed for calculations when a character has 2 pronoun sets
import re # regex
import shutil
import time # needed for pauses

alpha = re.compile("^[a-zA-Z]+$") # alphabetical characters only

# function for capitalizing the first letter of a String
def capitalize_first_let(s):
    cap = s[0].upper()
    if len(s) > 1:
        cap += s[1:len(s)]

    return cap

"""
Player class
"""
class Player:

    """
    When initializing, assign the Player's Name and associated Name Variables immediately.
    Create 3 empty dictionaries, 1 each for pronoun set #1, #2, and Gerudo Set pronouns.
    """
    def __init__(self, default="1", name="Link", nameD="Linky", nameZ="Linny"):

        # default = 1 or 2 (Link or Zelda, respectively)

        self.nameAttr = []
        self.default = default

        if default == "1":
            
            self.name = name
            self.nameD = nameD # Linky
            # nameD = name diminutive.
            # A genius scientist great-aunt turned six-year-old uses this for you.
            self.name2 = self.name[:2] # Li
            self.name3 = self.name[:3] # Lin

            redacted = ""
            i = 0
            while i < (len(self.name)-1):
                redacted += "-"
                i += 1
            self.nameRed = self.name[0] + redacted # L---
            # nameRed = redacted name
            
            self.nameZ = nameZ # Linny
            # nameZ = name Zora. A Zora childhood friend uses this for you.
            self.nameZY = self.nameZ + (3*self.nameZ[-1]) # Linnyyyy
            # nameZY = name Zora w/ extra Y's
            self.nameZB = self.name.upper() # LINK
            # nameZB = name Zora Bang (an ! is also known as a "bang")
        
        elif default == "2":
            self.name = "Zelda"
            self.nameD = "Zeldie"
            self.name2 = self.name[:3] # Zel
            self.name3 = self.name[:4] # Zeld

            redacted = ""
            i = 1
            while i <= (len(self.name)-1):
                redacted += "-"
                i += 1
            self.nameRed = self.name[0] + redacted # Z----

            self.nameZ = "Zeezee"
            self.nameZY = self.nameZ + (3*self.nameZ[-1]) # Zeezeeeee
            self.nameZB = self.name.upper() # ZELDA       
        
        else: # Allow alphabetical chars only, no spaces. Allow chars w/ accents, tildes, etc.
            """
            Unused.

            First attempt at an if-else clause for when the user wants to customize the Player's name.
            (The current plan is 1-6 characters long.)
            For now, the user can only pick between Link and Zelda.
            """

            self.name = name
            self.nameD = nameD
                        
            if len(name) == 1:
                self.name2 = "Uh"
                self.name3 = "Erm"

                self.nameRed = name
            elif len(name) == 2:
                self.name2 = name[0]
                self.name3 = name[0]

                self.nameRed = name[0] + "-"
            elif len(name) == 3:
                self.name2 = name[0]
                self.name3 = name[:2]

                self.nameRed = name[0] + "--"
            else:
                self.name2 = name[:2]
                self.name3 = name[:3]

                i = 1
                redacted = ""
                while i <= (len(name)-1):
                    redacted += "-"
                    i += 1
                self.nameRed = name[0] + redacted                
            
            self.nameZ = nameZ # PNameZora

            y = nameZ[len(nameZ)-1]
            yyy = y + y + y
            self.nameZY = nameZ + yyy # PNameZoraY

            self.nameZB = nameZ.upper() # PNameZora!
        
        # Add all name variations to the name attributes list, 'nameAttr'
        self.nameAttr.append(self.name)
        self.nameAttr.append(self.nameD)
        self.nameAttr.append(self.name2)
        self.nameAttr.append(self.name3)
        self.nameAttr.append(self.nameRed)
        self.nameAttr.append(self.nameZ)
        self.nameAttr.append(self.nameZY)
        self.nameAttr.append(self.nameZB)

        self.gender = "" # The user is prompted for this in the function playerAttr
        
        # Set the 3 empty pronoun dictionaries
        self.prns1 = {}
        self.prns2 = {}
        self.PV = {}
        self.prns = [self.prns1, self.prns2, self.PV]
        self.numPrns = 1

        self.prns_Tb = None

        # Set each key in each dictionary with an empty string as the value
        for d in self.prns:
            d["sub"] = ""
            d["obj"] = ""
            d["pd"] = ""
            d["pp"] = ""
            d["ref"] = ""
            d["bio"] = ""
            d["sp"] = ""
            d["percent"] = ""
        
        # separate dictionaries for singular or plural pronouns
        self.sing = {}
        self.plural = {}

        self.sing["[P.is]"] = " is"
        self.sing["[P.is<]"] = "is "
        self.sing["[P.is<^]"] = "Is "
        self.sing["[P.'s]"] = "'s"
        self.sing["[P.bs]"] = "\\nis"
        self.sing["[P.tru]"] = " truly\\nis"
        self.sing["[P.see]"] = " sees"
        self.sing["[P.need]"] = " needs"
        self.sing["[P.carry]"] = " carries"
        self.sing["[P.break]"] = " breaks"
        self.sing["[P.land]"] = " lands"
        self.sing["[P.ret]"] = "\\nreturns"
        self.sing["[P.has]"] = " has"
        self.sing["[P.nhas]"] = "\\nhas"
        self.sing["[P.'h]"] = "'s"
        self.sing["[P.fight]"] = " fights"
        self.sing["[P.lose]"] = " loses"
        self.sing["[P.was]"] = " was"
        self.sing["[P.nwas]"] = " was\\ncurious"
        self.sing["[P.spark]"] = " sparkles"
        self.sing["[P.shin]"] = " shines"
        self.sing["[P.want]"] = " wants"
        self.sing["[P.ante]"] = " antes"
        self.sing["[P.awake]"] = " awakens"
        self.sing["[P.com]"] = " comes"
        self.sing["[P.sleep]"] = " sleeps"
        self.sing["[P.leap]"] = " leaps"
        self.sing["[P.rknow]"] = "\\nreally knows"
        self.sing["[P.feel]"] = " feels"
        self.sing["[P.nock]"] = " comes by and nocks"
        self.sing["[P.rem]"] = " remembers"
        self.sing["[P.look]"] = " looks"
        self.sing["[P.stan]"] = " who stands"
        self.sing["[P.tr]"] = "is" #*
        self.sing["[P.dont]"] = " doesn't"
        self.sing["[P.alw]"] = " always does"
        self.sing["[P.do]"] = " does"
        self.sing["[P.tell]"] = " tells"
        self.sing["[P.know]"] = " knows"
        self.sing["[P.we]"] = " and I" # --> needs to be readjusted with the actual pronoun
        self.sing["[P.res]"] = " no\\nlonger resembles"
        self.sing["[P.hard]"] = " hardly speaks anymore, and smiles"
        self.sing["[P.face]"] = "\\nfaces"
        self.sing["[P.focus]"] = " focuses"
        self.sing["[P.wake]"] = "\\nwakes"
        self.sing["[P.lack]"] = "\\nlacks"

        self.plural["[P.is]"] = " are"
        self.plural["[P.is<]"] = "are "
        self.plural["[P.is<^]"] = "Are "
        self.plural["[P.'s]"] = "'re"
        self.plural["[P.bs]"] = "\\nare"
        self.plural["[P.tru]"] = "\\ntruly are"
        self.plural["[P.see]"] = " see"
        self.plural["[P.need]"] = " need"
        self.plural["[P.carry]"] = " carry"
        self.plural["[P.break]"] = " break"
        self.plural["[P.land]"] = " land"
        self.plural["[P.ret]"] = "\\nreturn"
        self.plural["[P.has]"] = " have"
        self.plural["[P.nhas]"] = "\\nhave"
        self.plural["[P.'h]"] = "'ve"
        self.plural["[P.fight]"] = " fight"
        self.plural["[P.lose]"] = " lose"
        self.plural["[P.was]"] = " were"
        self.plural["[P.nwas]"] = "\\nwere curious"
        self.plural["[P.spark]"] = " sparkle"
        self.plural["[P.shin]"] = " shine"
        self.plural["[P.want]"] = " want"
        self.plural["[P.ante]"] = " ante"
        self.plural["[P.awake]"] = " awaken"
        self.plural["[P.com]"] = " come"
        self.plural["[P.sleep]"] = " sleep"
        self.plural["[P.leap]"] = " leap"
        self.plural["[P.rknow]"] = "\\nreally know"
        self.plural["[P.feel]"] = " feel"
        self.plural["[P.nock]"] = " come by and nock"
        self.plural["[P.rem]"] = " remember"
        self.plural["[P.look]"] = " look"
        self.plural["[P.stan]"] = " who stand"
        self.plural["[P.tr]"] = " are" # --> needs to be readjusted with the actual pronoun
        self.plural["[P.dont]"] = " don't"
        self.plural["[P.alw]"] = " always do"
        self.plural["[P.do]"] = " do"
        self.plural["[P.tell]"] = " tell"
        self.plural["[P.know]"] = " know"
        self.plural["[P.we]"] = "we"
        self.plural["[P.res]"] = " no\\nlonger resemble"
        self.plural["[P.hard]"] = " hardly speak anymore, and smile"
        self.plural["[P.face]"] = "\\nface"
        self.plural["[P.focus]"] = " focus"
        self.plural["[P.wake]"] = "\\nwake"
        self.plural["[P.lack]"] = "\\nlack"


        # Vai pronouns
        self.PV_sing = {} # singular
        self.PV_plural = {} # separate dictionary for whether "vai" pronouns are singular or plural
        
        self.PV_sing["[P.isV]"] = " is"
        self.PV_sing["[P.is<V]"] = "is "
        self.PV_sing["[P.'sV]"] = "'s"
        self.PV_sing["[P.evenV]"] = " even has"

        self.PV_plural["[P.isV]"] = " are"
        self.PV_plural["[P.is<V]"] = "are "
        self.PV_plural["[P.'sV]"] = "'re"
        self.PV_plural["[P.evenV]"] = " even have"
    
    # After taking User input, set those values as the Player's pronouns.
    # prnSet distinguishes which set of pronouns (1 or 2) is being set.
    def set_player_prns(self, prnSet, sub="he", obj="him", pd="his", pp="his", ref="himself", sp="1", percent="N/A"):
        prnSet["sub"] = sub.lower()
        prnSet["obj"] = obj.lower()
        prnSet["pd"] = pd.lower()
        prnSet["pp"] = pp.lower()
        prnSet["ref"] = ref.lower()
        prnSet["bio"] = prnSet["sub"] + "/" + prnSet["obj"] + "/" + prnSet["pp"] # e.g., he/him/his (pronouns in bio)

        if sp == "1": # denotes Singular pronouns, e.g., he is, he goes
            prnSet["sp"] = "Singular"
        elif sp == "2": # denotes Plural pronouns, e.g., they are, they go
            prnSet["sp"] = "Plural"
        
        # denote percentage of the amount of time these pronouns are seen in-game
        prnSet["percent"] = percent

    # After taking User input, set those values as the Player's pronouns while they are
    # wearing the Gerudo Set.
    # For brevity, these pronouns are sometimes referred to in this program as "vai pronouns"
    def set_vai_prns(self, sub="she", obj ="her", pd="hers", sp="1"):
        
        self.PV["sub"] = sub.lower()
        self.PV["obj"] = obj.lower()
        self.PV["pd"] = pd.lower()
        self.PV["pp"] = "N/A"
        self.PV["ref"] = "N/A"
        self.PV["bio"] = self.PV["sub"] + "/" + self.PV["obj"]

        if sp == "1":
            self.PV["sp"] = "Singular"
        elif sp == "2":
            self.PV["sp"] = "Plural"

        self.PV["percent"] = "N/A"
       

    def set_replace_dict(self):

        # Load the dictionaries for name and Gerudo Set pronouns first, since they're less complicated

        # Create the name dictionary
        self.replace_names = {} # dictionary for name and name derivatives
        self.replace_names["[PName]"] = self.name
        self.replace_names["[PNameDim]"] = self.nameD
        self.replace_names["[PName2]"] = self.name2
        self.replace_names["[PName3]"] = self.name3
        self.replace_names["[PNameRed]"] = self.nameRed
        self.replace_names["[PNameZ]"] = self.nameZ
        self.replace_names["[PNameZy]"] = self.nameZY
        self.replace_names["[PNameZ!]"] = self.nameZB
        

        # Create the Gerudo Set pronouns dictionary
        self.replace_PV = {} # dictionary for "vai" (Gerudo Set) pronouns
        self.replace_PV["[P.01SubV]"] = self.PV["sub"]

        # first char capitalized only
        self.replace_PV["[P.01Sub^V]"] = capitalize_first_let(self.PV["sub"])
        
        self.replace_PV["[P.01Sub^^V]"] = (self.PV["sub"]).upper()
        self.replace_PV["[P.02ObjV]"] = self.PV["obj"]
        self.replace_PV["[P.02Obj^^V]"] = (self.PV["obj"]).upper()
        self.replace_PV["[P.03PDV]"] = self.PV["pd"]

        if self.PV["sp"] == "Singular": # If the "vai" pronouns are singular
            for a in self.PV_sing:
                self.replace_PV[a] = self.PV_sing[a]
        else: # If the "vai" pronouns are plural
            for a in self.PV_plural:
                self.replace_PV[a] = self.PV_plural[a]
        

        self.replace_dict_1 = {} # dictionary for default pronoun set #1
        self.replace_dict_2 = {} # dictionary for default pronoun set #2 (if applicable)
        self.replace_combo = {} # dictionary for both default pronoun sets (if applicable)

        
        if self.numPrns == 1: # If the Player has only one set of pronouns

            # In the case of a single pronoun set, the order in which variables
            # are replaced doesn't matter, as opposed to the order in which
            # variables in multiple pronoun sets are replaced.
            
            # This is because for a single pronoun set, each variable can
            # be separated; e.g., "he goes" can easily be separated into "he" and "goes."

            # For instances of multiple pronoun sets, variables must remain
            # grouped together, hence the specific variable replacement order. 
            # For example, if the Player uses he/they pronouns, an instance of
            # "He goes" should be replaced with either "He goes" or "They go."
            # Appropriate organization and replacement order prevents errors
            # such as the sentence "He goes" being replaced with "He go" or "They goes."
            self.replace_dict_1["[P.01Sub]"] = self.prns1["sub"]

            self.replace_dict_1["[P.01Sub^]"] = capitalize_first_let(self.prns1["sub"]) #p1_subCap
            
            self.replace_dict_1["[P.01Sub^^]"] = self.prns1["sub"].upper()
            self.replace_dict_1["[P.02Obj]"] = self.prns1["obj"]
            
            self.replace_dict_1["[P.02Obj^]"] = self.prns1["obj"].upper()

            self.replace_dict_1["[P.03PD]"] = self.prns1["pd"]

            self.replace_dict_1["[P.03PD^]"] = capitalize_first_let(self.prns1["pd"])

            self.replace_dict_1["[P.04PP]"] = self.prns1["pp"]
            self.replace_dict_1["[P.05Ref]"] = self.prns1["ref"]


            # Singular or plural pronouns
            if self.prns1["sp"] == "Singular": # If the default pronouns 1 are singular
                self.sing["[P.we]"] = self.prns1["sub"] + self.sing["[P.we]"] #[sub] and I
                for b in self.sing:
                    self.replace_dict_1[b] = self.sing[b]
                
            else: # If the default pronouns 1 are plural
                self.plural["[P.tr]"] = self.prns1["sub"] + self.plural["[P.tr]"] #[sub] are
                for b in self.plural:
                    self.replace_dict_1[b] = self.plural[b]

        else: # If the Player has two sets of pronouns
            self.replace_dict_1["[P.01Sub]"] = self.prns1["sub"]
            
            self.replace_dict_1["[P.01Sub^]"] = capitalize_first_let(self.prns1["sub"])
            
            self.replace_dict_1["[P.01Sub^^]"] = self.prns1["sub"].upper()
            self.replace_dict_1["[P.02Obj]"] = self.prns1["obj"]

            self.replace_dict_1["[P.02Obj^]"] = self.prns1["obj"].upper()

            self.replace_dict_1["[P.03PD]"] = self.prns1["pd"]

            self.replace_dict_1["[P.03PD^]"] = capitalize_first_let(self.prns1["pd"])

            self.replace_dict_1["[P.04PP]"] = self.prns1["pp"]
            self.replace_dict_1["[P.05Ref]"] = self.prns1["ref"]

            # Singular or plural next.
            if self.prns1["sp"] == "Singular": # If the default pronouns 1 are singular
                self.sing["[P.we]"] = self.prns1["sub"] + self.sing["[P.we]"] #[sub] and I
                for b in self.sing:
                    self.replace_dict_1[b] = self.sing[b]
                
            else: # If the default pronouns 1 are plural
                self.plural["[P.tr]"] = self.prns1["sub"] + self.plural["[P.tr]"] #[sub] are                
                for b in self.plural:
                    self.replace_dict_1[b] = self.plural[b]


            # Next, due the same for prns2
            self.replace_dict_2["[P.01Sub]"] = self.prns2["sub"]
            
            self.replace_dict_2["[P.01Sub^]"] = capitalize_first_let(self.prns2["sub"])
            
            self.replace_dict_2["[P.01Sub^^]"] = self.prns2["sub"].upper()
            self.replace_dict_2["[P.02Obj]"] = self.prns2["obj"]

            self.replace_dict_2["[P.02Obj^]"] = self.prns2["obj"].upper()

            self.replace_dict_2["[P.03PD]"] = self.prns2["pd"]

            self.replace_dict_2["[P.03PD^]"] = capitalize_first_let(self.prns2["pd"])

            self.replace_dict_2["[P.04PP]"] = self.prns2["pp"]
            self.replace_dict_2["[P.05Ref]"] = self.prns2["ref"]

            # Singular or plural next.
            if self.prns2["sp"] == "Singular": # If the default pronouns 1 are singular
                self.sing["[P.we]"] = self.prns2["sub"] + self.sing["[P.we]"] #[sub] and I, e.g., "she and I"
                for b in self.sing:
                    self.replace_dict_2[b] = self.sing[b]
                
            else: # If the default pronouns 1 are plural
                self.plural["[P.tr]"] = self.prns2["sub"] + self.plural["[P.tr]"] #[sub] are
                for b in self.plural:
                    self.replace_dict_2[b] = self.plural[b]

            # Now, combine both pronoun sets into one replacement dictionary.
            # This dictionary is subject to change as more templates are completed.
            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.is]"] #He is
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.is]"]
            self.replace_combo["[P.01Sub^][P.is]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.is]"] #he is
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.is]"]
            self.replace_combo["[P.01Sub][P.is]"] = [a, b]

            a = self.replace_dict_1["[P.is<]"] + self.replace_dict_1["[P.01Sub]"] #is he
            b = self.replace_dict_2["[P.is<]"] + self.replace_dict_2["[P.01Sub]"]
            self.replace_combo["[P.is<][P.01Sub]"] = [a, b]

            a = self.replace_dict_1["[P.is<^]"] + self.replace_dict_1["[P.01Sub]"] #Is he
            b = self.replace_dict_2["[P.is<^]"] + self.replace_dict_2["[P.01Sub]"]
            self.replace_combo["[P.is<^][P.01Sub]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.'s]"] #he's (he is)
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.'s]"]
            self.replace_combo["[P.01Sub][P.'s]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.bs]"] #he\nis
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.bs]"]
            self.replace_combo["[P.01Sub][P.bs]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.'s]"] #He's (He is)
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.'s]"]
            self.replace_combo["[P.01Sub^][P.'s]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.tru]"] #he truly\nis
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.tru]"]
            self.replace_combo["[P.01Sub][P.tru]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.see]"] #he sees
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.see]"]
            self.replace_combo["[P.01Sub][P.see]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.need]"] #he needs
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.need]"]
            self.replace_combo["[P.01Sub][P.need]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.carry]"] #he carries
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.carry]"]
            self.replace_combo["[P.01Sub][P.carry]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.carry]"] #He carries
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.carry]"]
            self.replace_combo["[P.01Sub^][P.carry]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.break]"] #He breaks
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.break]"]
            self.replace_combo["[P.01Sub^][P.break]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.land]"] #He lands
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.land]"]
            self.replace_combo["[P.01Sub^][P.land]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.ret]"] #he\nreturns
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.ret]"]
            self.replace_combo["[P.01Sub][P.ret]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.has]"] #he has
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.has]"]
            self.replace_combo["[P.01Sub][P.has]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.nhas]"] #he\nhas
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.nhas]"]
            self.replace_combo["[P.01Sub][P.nhas]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.'h]"] #he's (he has)
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.'h]"]
            self.replace_combo["[P.01Sub][P.'h]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.has]"] #He has
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.has]"]
            self.replace_combo["[P.01Sub^][P.has]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.'h]"] #He's (He has)
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.'h]"]
            self.replace_combo["[P.01Sub^][P.'h]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.fight]"] #he fights
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.fight]"]
            self.replace_combo["[P.01Sub][P.fight]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.lose]"] #he loses
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.lose]"]
            self.replace_combo["[P.01Sub][P.lose]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.was]"] #He was
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.was]"]
            self.replace_combo["[P.01Sub^][P.was]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.was]"] #he was
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.was]"]
            self.replace_combo["[P.01Sub][P.was]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.nwas]"] #He was\ncurious
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.nwas]"]
            self.replace_combo["[P.01Sub^][P.nwas]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.spark]"] #He sparkles
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.spark]"]
            self.replace_combo["[P.01Sub^][P.spark]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.shin]"] #He shines
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.shin]"]
            self.replace_combo["[P.01Sub^][P.shin]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.want]"] #he wants
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.want]"]
            self.replace_combo["[P.01Sub][P.want]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.ante]"] #he antes
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.ante]"]
            self.replace_combo["[P.01Sub][P.ante]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.awake]"] #he awakens
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.awake]"]
            self.replace_combo["[P.01Sub][P.awake]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.com]"] #he comes
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.com]"]
            self.replace_combo["[P.01Sub][P.com]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.sleep]"] #he sleeps
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.sleep]"]
            self.replace_combo["[P.01Sub][P.sleep]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.leap]"] #he leaps
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.leap]"]
            self.replace_combo["[P.01Sub][P.leap]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.rknow]"] #he\nreally knows
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.rknow]"]
            self.replace_combo["[P.01Sub][P.rknow]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.feel]"] #he feels
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.feel]"]
            self.replace_combo["[P.01Sub][P.feel]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.nock]"] #he comes by and nocks
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.nock]"]
            self.replace_combo["[P.01Sub][P.nock]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.rem]"] #He remembers
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.rem]"]
            self.replace_combo["[P.01Sub^][P.rem]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.look]"] #he looks
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.look]"]
            self.replace_combo["[P.01Sub][P.look]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.stan]"] #He who stands
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.stan]"]
            self.replace_combo["[P.01Sub^][P.stan]"] = [a, b]

            a = self.replace_dict_1["[P.tr]"] #is (plural: [sub] are)
            b = self.replace_dict_2["[P.tr]"]
            self.replace_combo["[P.tr]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.dont]"] #he doesn't
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.dont]"]
            self.replace_combo["[P.01Sub][P.dont]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.alw]"] #he always does
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.alw]"]
            self.replace_combo["[P.01Sub][P.alw]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.do]"] #he does
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.do]"]
            self.replace_combo["[P.01Sub][P.do]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.tell]"] #He tells
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.tell]"]
            self.replace_combo["[P.01Sub^][P.tell]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.know]"] #he knows
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.know]"]
            self.replace_combo["[P.01Sub][P.know]"] = [a, b]

            a = self.replace_dict_1["[P.we]"] #[sub] and I (plural: we)
            b = self.replace_dict_2["[P.we]"]
            self.replace_combo["[P.we]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.res]"] #He no\nlonger resembles
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.res]"]
            self.replace_combo["[P.01Sub^][P.res]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub^]"] + self.replace_dict_1["[P.hard]"] #He hardly speaks anymore, and smiles
            b = self.replace_dict_2["[P.01Sub^]"] + self.replace_dict_2["[P.hard]"]
            self.replace_combo["[P.01Sub^][P.hard]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.face]"] #he\nfaces
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.face]"]
            self.replace_combo["[P.01Sub][P.face]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.focus]"] #he focuses
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.focus]"]
            self.replace_combo["[P.01Sub][P.focus]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.wake]"] #he\nwakes
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.wake]"]
            self.replace_combo["[P.01Sub][P.wake]"] = [a, b]

            a = self.replace_dict_1["[P.01Sub]"] + self.replace_dict_1["[P.lack]"] #he\nlacks
            b = self.replace_dict_2["[P.01Sub]"] + self.replace_dict_2["[P.lack]"]
            self.replace_combo["[P.01Sub][P.lack]"] = [a, b]


            # Less complicated combos

            # These 3 I moved down here from line 508.
            # Otherwise, when counting instances, these ones will be double counted.
            # e.g., "[P.01Sub]" could be found by itself first, then found again in "[P.01Sub][P.lack]" later and then counted twice...
            # There is a way to circumvent the counting issue, by doing a bit of math.
            # But this order is actually needed for *replacing* the correct variables.
            self.replace_combo["[P.01Sub]"] = [self.replace_dict_1["[P.01Sub]"], self.replace_dict_2["[P.01Sub]"]]
            self.replace_combo["[P.01Sub^]"] = [self.replace_dict_1["[P.01Sub^]"], self.replace_dict_2["[P.01Sub^]"]]
            self.replace_combo["[P.01Sub^^]"] = [self.replace_dict_1["[P.01Sub^^]"], self.replace_dict_2["[P.01Sub^^]"]]

            self.replace_combo["[P.02Obj]"] = [self.replace_dict_1["[P.02Obj]"], self.replace_dict_2["[P.02Obj]"]]

            self.replace_combo["[P.02Obj^]"] = [self.replace_dict_1["[P.02Obj^]"], self.replace_dict_2["[P.02Obj^]"]]

            self.replace_combo["[P.03PD]"] = [self.replace_dict_1["[P.03PD]"], self.replace_dict_2["[P.03PD]"]]

            self.replace_combo["[P.03PD^]"] = [self.replace_dict_1["[P.03PD^]"], self.replace_dict_2["[P.03PD^]"]]

            self.replace_combo["[P.04PP]"] = [self.replace_dict_1["[P.04PP]"], self.replace_dict_2["[P.04PP]"]]
            self.replace_combo["[P.05Ref]"] = [self.replace_dict_1["[P.05Ref]"], self.replace_dict_2["[P.05Ref]"]]
        
# Class for creating a Keeper object (Zelda's role in the base game)
class Keeper:
    
    def __init__(self, default="1", name=""):
        
        self.default = default

        if default == "1":            
            self.name = "Zelda"       
        elif default == "2":
            self.name = "Link"        
        else: # Allow alphabetical chars only, no spaces. Allow chars w/ accents, tildes, etc.
            """
            Unused.

            Draft for an if-else clause for when the user wants to customize the Player's name.
            (The current plan is 1-6 characters long.)
            For now, the user can only pick between Link and Zelda.
            """
            self.name = name                

        self.gender = "" # The user is prompted for this in the function keeperAttr
        
        # Set the 2 empty pronoun dictionaries

        self.prns_Tb = None
        # Notice there are no pronouns for when the Keeper is specifically wearing the Gerudo Set.
        # This is because the Keeper does not wear the Gerudo Set in the game.

        # Set each key in each dictionary with an empty string as the value
        
        self.prns1_2 = {}
        self.prns2_2 = {}
        self.prns_2 = [self.prns1_2, self.prns2_2]
        self.numPrns = 1 # number of pronoun sets the Keeper has. e.g., "she/her" = 1; "he/they" = 2
        
        # Streamline User prompts
        for d in self.prns_2:
            d["sub"] = ["", 4, "Please enter the Keeper's subjective pronoun (1-4 characters).\
                \nExamples: she (default), he, they\
                \nExample sentence: *She* conducts tech research."]
            
            d["obj"] = ["", 4, "Please enter the Keeper's objective pronoun (1-4 characters).\
                \nExamples: her (default), him, them\
                \nExample sentence: I gave *her* a haircut."]
            
            d["pd"] = ["", 5, "Please enter the Keeper's possessive determiner (1-5 characters).\
                \nExamples: her (default), his, their\
                \nExample sentence: I fueled up *her* motorcycle."]                  
            
            d["ref"] = ["", 8, "Please enter the Keeper's reflexive pronoun (1-8 characters).\
                \nExamples: herself (default), himself, themself\
                \nExample sentence: She smiled to *herself.*"]
            
            d["bio"] = ""
            d["sp"] = ""
            d["percent"] = ""

        # singular or plural pronouns
        self.sing = {}
        self.plural = {}

        self.sing["[K.is]"] = " is"
        self.sing["[K.'s]"] = "'s"
        self.sing["[K.bs]"] = "\\nis"
        self.sing["[K.need]"] = " needs"
        self.sing["[K.ret]"] = " returns"
        self.sing["[K.has]"] = " has"
        self.sing["[K.'h]"] = "'s"
        self.sing["[K.was]"] = " was"
        self.sing["[K.com]"] = " comes"
        self.sing["[K.feel]"] = " feels"
        self.sing["[K.look]"] = " looks up and sees"
        self.sing["[K.do]"] = " does"
        self.sing["[K.we]"] = " and I"
        self.sing["[K.really]"] = " really is"
        self.sing["[K.att]"] = " attempts"
        self.sing["[K.expr]"] = " then expresses"
        self.sing["[K.expl]"] = " explains"
        self.sing["[K.catch]"] = " also catches"
        self.sing["[K.open]"] = " opens"
        self.sing["[K.wit]"] = " witnesses"
        self.sing["[K.instr]"] = " instructs"
        self.sing["[K.end]"] = " endures"
        self.sing["[K.cont]"] = " continues"
        self.sing["[K.get]"] = " gets"
        self.sing["[K.work]"] = " works"
        self.sing["[K.call]"] = " calls"
        self.sing["[K.bel]"] = " believes"
        self.sing["[K.try]"] = " tries"
        self.sing["[K.give]"] = " ever gives"
        self.sing["[K.claim]"] = " claims"
        self.sing["[K.go]"] = " goes"
        self.sing["[K.wish]"] = " wishes"

        self.plural["[K.is]"] = " are"
        self.plural["[K.'s]"] = "'re"
        self.plural["[K.bs]"] = "\\nare"
        self.plural["[K.need]"] = " need"
        self.plural["[K.ret]"] = " return"
        self.plural["[K.has]"] = " have"
        self.plural["[K.'h]"] = "'ve"
        self.plural["[K.was]"] = " were"
        self.plural["[K.com]"] = " come"
        self.plural["[K.feel]"] = " feel"
        self.plural["[K.look]"] = " look up and see"
        self.plural["[K.do]"] = " do"
        self.plural["[K.we]"] = "we"
        self.plural["[K.really]"] = " really are"
        self.plural["[K.att]"] = " attempt"
        self.plural["[K.expr]"] = " then express"
        self.plural["[K.expl]"] = " explain"
        self.plural["[K.catch]"] = " also catch"
        self.plural["[K.open]"] = " open"
        self.plural["[K.wit]"] = " witness"
        self.plural["[K.instr]"] = " instruct"
        self.plural["[K.end]"] = " endure"
        self.plural["[K.cont]"] = " continue"
        self.plural["[K.get]"] = " get"
        self.plural["[K.work]"] = " work"
        self.plural["[K.call]"] = " call"
        self.plural["[K.bel]"] = " believe"
        self.plural["[K.try]"] = " try"
        self.plural["[K.give]"] = " ever give"
        self.plural["[K.claim]"] = " claim"
        self.plural["[K.go]"] = " go"
        self.plural["[K.wish]"] = " wish"
    
    # After taking User input, set those values as the Keeper's pronouns.
    # prnSet distinguishes which set of pronouns (1 or 2) is being set.
    # Note that the Keeper's pronouns are stored within a dictionary of lists of strings,
    # whereas the Player's pronouns are stored within a dictionary of strings.
    # There is no particular reason for this other than testing different methods
    # of storing these attributes. The method used for the Keeper's pronouns
    # may be somewhat cleaner.
    def set_keeper_prns(self, prnSet, sub="she", obj="her", pd="her", ref="herself", sp="1", percent="N/A"):
        
        prnSet["sub"][0] = sub        
        prnSet["obj"][0] = obj
        prnSet["pd"][0] = pd        
        prnSet["ref"][0] = ref
        prnSet["bio"] = prnSet["sub"][0] + "/" + prnSet["obj"][0]

        if sp == "1":
            prnSet["sp"] = "Singular"
        elif sp == "2":
            prnSet["sp"] = "Plural"
        
        prnSet["percent"] = percent
    
    def set_replace_dict(self):

        self.replace_dict_1 = {}
        self.replace_dict_2 = {}
        self.replace_combo = {}

        if self.numPrns == 1:

            # Pronouns themselves first
            self.replace_dict_1["[K.01Sub]"] = self.prns1_2["sub"][0]
            self.replace_dict_1["[K.01Sub^]"] = capitalize_first_let(self.prns1_2["sub"][0])

            self.replace_dict_1["[K.02Obj]"] = self.prns1_2["obj"][0]
            self.replace_dict_1["[K.03PD]"] = self.prns1_2["pd"][0]
            self.replace_dict_1["[K.03PD^]"] = capitalize_first_let(self.prns1_2["pd"][0])
            self.replace_dict_1["[K.05Ref]"] = self.prns1_2["ref"][0]

            if self.prns1_2["sp"] == "Singular": # If the default pronouns 1 are singular
                self.sing["[K.we]"] = self.prns1_2["sub"][0] + self.sing["[K.we]"] #[sub] and I
                for b in self.sing:
                    self.replace_dict_1[b] = self.sing[b]
                
            else: # If the default pronouns 1 are plural
                for b in self.plural:
                    self.replace_dict_1[b] = self.plural[b]

        else:

            self.replace_dict_1["[K.01Sub]"] = self.prns1_2["sub"][0]
            self.replace_dict_1["[K.01Sub^]"] = capitalize_first_let(self.prns1_2["sub"][0])

            self.replace_dict_1["[K.02Obj]"] = self.prns1_2["obj"][0]
            self.replace_dict_1["[K.03PD]"] = self.prns1_2["pd"][0]
            self.replace_dict_1["[K.03PD^]"] = capitalize_first_let(self.prns1_2["pd"][0])
            self.replace_dict_1["[K.05Ref]"] = self.prns1_2["ref"][0]

            if self.prns1_2["sp"] == "Singular": # If the default pronouns 1 are singular
                self.sing["[K.we]"] = self.prns1_2["sub"][0] + self.sing["[K.we]"] #[sub] and I
                for b in self.sing:
                    self.replace_dict_1[b] = self.sing[b]
                
            else: # If the default pronouns 1 are plural
                for b in self.plural:
                    self.replace_dict_1[b] = self.plural[b]

            # prns2 next
            self.replace_dict_2["[K.01Sub]"] = self.prns2_2["sub"][0]
            self.replace_dict_2["[K.01Sub^]"] = capitalize_first_let(self.prns2_2["sub"][0])

            self.replace_dict_2["[K.02Obj]"] = self.prns2_2["obj"][0]
            self.replace_dict_2["[K.03PD]"] = self.prns2_2["pd"][0]
            self.replace_dict_2["[K.03PD^]"] = capitalize_first_let(self.prns2_2["pd"][0])
            self.replace_dict_2["[K.05Ref]"] = self.prns2_2["ref"][0]

            if self.prns2_2["sp"] == "Singular": # If the default pronouns 1 are singular
                self.sing["[K.we]"] = self.prns2_2["sub"][0] + self.sing["[K.we]"] #[sub] and I
                for b in self.sing:
                    self.replace_dict_2[b] = self.sing[b]
                
            else: # If the default pronouns 1 are plural
                for b in self.plural:
                    self.replace_dict_2[b] = self.plural[b]
            
            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.is]"] #she is
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.is]"]
            self.replace_combo["[K.01Sub][K.is]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.'s]"] #she's
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.'s]"]
            self.replace_combo["[K.01Sub][K.'s]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.bs]"] #she\nis
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.bs]"]
            self.replace_combo["[K.01Sub][K.bs]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.'s]"] #She's
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.'s]"]
            self.replace_combo["[K.01Sub^][K.'s]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.really]"] #She really is
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.really]"]
            self.replace_combo["[K.01Sub^][K.really]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.att]"] #She attempts
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.att]"]
            self.replace_combo["[K.01Sub^][K.att]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.att]"] #she attempts
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.att]"]
            self.replace_combo["[K.01Sub][K.att]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.need]"] #she needs
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.need]"]
            self.replace_combo["[K.01Sub][K.need]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.expr]"] #She then expresses
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.expr]"]
            self.replace_combo["[K.01Sub^][K.expr]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.expl]"] #She explains
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.expl]"]
            self.replace_combo["[K.01Sub^][K.expl]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.catch]"] #She also catches
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.catch]"]
            self.replace_combo["[K.01Sub^][K.catch]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.open]"] #she opens
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.open]"]
            self.replace_combo["[K.01Sub][K.open]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.has]"] #she has
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.has]"]
            self.replace_combo["[K.01Sub][K.has]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.'h]"] #she's (she has)
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.'h]"]
            self.replace_combo["[K.01Sub][K.'h]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.has]"] #She has
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.has]"]
            self.replace_combo["[K.01Sub^][K.has]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.'h]"] #She's (She has)
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.'h]"]
            self.replace_combo["[K.01Sub^][K.'h]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.wit]"] #she witnesses
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.wit]"]
            self.replace_combo["[K.01Sub][K.wit]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.instr]"] #She instructs
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.instr]"]
            self.replace_combo["[K.01Sub^][K.instr]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.end]"] #She endures
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.end]"]
            self.replace_combo["[K.01Sub^][K.end]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.cont]"] #She continues
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.cont]"]
            self.replace_combo["[K.01Sub^][K.cont]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.was]"] #She was
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.was]"]
            self.replace_combo["[K.01Sub^][K.was]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.was]"] #she was
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.was]"]
            self.replace_combo["[K.01Sub][K.was]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.get]"] #She gets
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.get]"]
            self.replace_combo["[K.01Sub^][K.get]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.look]"] #she looks up and sees
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.look]"]
            self.replace_combo["[K.01Sub][K.look]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.work]"] #she works
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.work]"]
            self.replace_combo["[K.01Sub][K.work]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.call]"] #she calls
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.call]"]
            self.replace_combo["[K.01Sub][K.call]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.com]"] #she comes
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.com]"]
            self.replace_combo["[K.01Sub][K.com]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.bel]"] #she believes
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.bel]"]
            self.replace_combo["[K.01Sub][K.bel]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.ret]"] #she returns
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.ret]"]
            self.replace_combo["[K.01Sub][K.ret]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.try]"] #She tries
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.try]"]
            self.replace_combo["[K.01Sub^][K.try]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.feel]"] #she feels
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.feel]"]
            self.replace_combo["[K.01Sub][K.feel]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.give]"] #she ever gives
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.give]"]
            self.replace_combo["[K.01Sub][K.give]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub^]"] + self.replace_dict_1["[K.claim]"] #She claims
            b = self.replace_dict_2["[K.01Sub^]"] + self.replace_dict_2["[K.claim]"]
            self.replace_combo["[K.01Sub^][K.claim]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.do]"] #she does
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.do]"]
            self.replace_combo["[K.01Sub][K.do]"] = [a, b]

            a = self.replace_dict_1["[K.we]"] #she and I (plural: we)
            b = self.replace_dict_2["[K.we]"]
            self.replace_combo["[K.we]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.go]"] #she goes
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.go]"]
            self.replace_combo["[K.01Sub][K.go]"] = [a, b]

            a = self.replace_dict_1["[K.01Sub]"] + self.replace_dict_1["[K.wish]"] #she wishes
            b = self.replace_dict_2["[K.01Sub]"] + self.replace_dict_2["[K.wish]"]
            self.replace_combo["[K.01Sub][K.wish]"] = [a, b]

            # Less complicated combos

            # 2 moved from line 1005.
            self.replace_combo["[K.01Sub]"] = [self.replace_dict_1["[K.01Sub]"], self.replace_dict_2["[K.01Sub]"]]
            self.replace_combo["[K.01Sub^]"] = [self.replace_dict_1["[K.01Sub^]"], self.replace_dict_2["[K.01Sub^]"]]

            self.replace_combo["[K.02Obj]"] = [self.replace_dict_1["[K.02Obj]"], self.replace_dict_2["[K.02Obj]"]]
            self.replace_combo["[K.03PD]"] = [self.replace_dict_1["[K.03PD]"], self.replace_dict_2["[K.03PD]"]]
            self.replace_combo["[K.03PD^]"] = [self.replace_dict_1["[K.03PD^]"], self.replace_dict_2["[K.03PD^]"]]
            self.replace_combo["[K.05Ref]"] = [self.replace_dict_1["[K.05Ref]"], self.replace_dict_2["[K.05Ref]"]]


# A miniscule pause lasting 0.1 seconds.
def miniPause():
    time.sleep(0.1)

"""
Function for generically confirming with user that their input is correct.
"""
def confirmation():
    while True:
        time.sleep(0.5)
        confirm = input("Is this correct? Y/N: ")

        if confirm.lower() == "y" or confirm.lower() == "yes":            
            return True
        elif confirm.lower() == "n" or confirm.lower() == "no":
            return False
        else:
            miniPause()
            print("Error: Please answer with either \"yes\" or \"no.\"")

# Prompt user for Player attributes here.
def playerAttr():
    print("\nDistilling Player Attributes...\n======")
    time.sleep(0.7)
    print("\nLet's enter the Player's name.")

    nameCorr = False # "correct"/"confirmation" variable specifically for picking the Player's Name
    """
    While loop for choosing the Player's Name
    """
    time.sleep(0.7)
    while not nameCorr:
        print("\nThe Player's name is...\
            \n1 = Link (default)\
            \n2 = Zelda\
            \n3 = Custom")
        time.sleep(0.7)
        name = input("Your answer: ")
        
        if name == "1":
            player = Player()

            nameTb = PrettyTable(["Player Name", "Your Input"]) # This table setting should be moved out of the if-else blocks.
            nameTb.add_row(["Full Name", player.name + " (default)"])
            nameTb.add_row(["Nickname from a genius scientist great-\naunt turned six-year-old. Check it!", player.nameD + " (default)"])
            nameTb.add_row(["Nickname from a Zora childhood friend.", player.nameZ + " (default)"])
            
            time.sleep(0.5)
            print("\nThe Player's default name and nicknames are shown below.")
            time.sleep(0.5)
            print()
            print(nameTb)
            
            time.sleep(1)
            nameCorr = confirmation()
            
        elif name == "2":
            player = Player("2")

            nameTb = PrettyTable(["Player Name", "Your Input"])
            nameTb.add_row(["Full Name", player.name])
            nameTb.add_row(["Nickname from a genius scientist great-\naunt turned six-year-old. Check it!", player.nameD])
            nameTb.add_row(["Nickname from a Zora childhood friend.", player.nameZ])
            
            time.sleep(0.5)
            print("\nThe Player's name and nicknames are shown below.")
            time.sleep(0.5)
            print()
            print(nameTb)
            
            time.sleep(1)
            nameCorr = confirmation()

        elif name == "3":
            print("Name customization screen activated.")
            
            #cNameCorr = False # variable for confirming the *c*ustom *Name* is *corr*ect
            #while not cNameCorr:
            while True:
                print("Please enter a name for the Player (1-8 characters).")
                time.sleep(1.6)
                cName = input("Your answer: ")

                if len(cName) < 1:
                    miniPause()
                    print("Error: Please enter at least 1 letter.\n")
                elif len(cName) > 8:
                    miniPause()
                    print("Error: Please enter no more than 8 letters.\n")
                elif alpha.match(cName) == None:
                    miniPause()
                    print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                else:
                    print()
                    break
            
            while True:
                print("Please enter a nickname given to the Player by a genius scientist\
                    \ngreat-aunt turned six-year-old. Check it! (1-6 characters)")
                time.sleep(1.6)
                cNameD = input("Your answer: ")

                if len(cNameD) < 1:
                    miniPause()
                    print("Error: Please enter at least 1 letter.\n")
                elif len(cNameD) > 6:
                    miniPause()
                    print("Error: Please enter no more than 6 letters.\n")
                elif alpha.match(cNameD) == None:
                    miniPause()
                    print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                else:
                    print()
                    break
            
            while True:
                print("Please enter a nickname given to the Player by a\
                    \nZora childhood friend (1-6 characters).")
                time.sleep(1.6)
                cNameZ = input("Your answer: ")

                if len(cNameZ) < 1:
                    miniPause()
                    print("Error: Please enter at least 1 letter.\n")
                elif len(cNameZ) > 6:
                    miniPause()
                    print("Error: Please enter no more than 6 letters.\n")
                elif alpha.match(cNameZ) == None:
                    miniPause()
                    print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                else:
                    print()
                    break

            nameTb = PrettyTable(["Player Name", "Your Input"]) # This table setting should be moved out of the if-else blocks.
            nameTb.add_row(["Full Name", cName])
            nameTb.add_row(["Nickname from a genius scientist great-\naunt turned six-year-old. Check it!", cNameD])
            nameTb.add_row(["Nickname from a Zora childhood friend.", cNameZ])

            time.sleep(0.5)
            print("\nThe Player's name and nicknames are shown below.")
            time.sleep(0.5)
            print()
            print(nameTb)
            
            time.sleep(1)
            nameCorr = confirmation()

            if nameCorr:
                player = Player("3", cName, cNameD, cNameZ)

        else:
            miniPause()
            print("Error: Please enter an option from the list provided.")

    time.sleep(0.7)
    print("\n------\nNext, let's enter the Player's gender.")
    genCorr = False # "correct"/"confirmation" variable specifically for picking the Player's Gender
    """
    While loop for entering the Player's Gender
    """
    time.sleep(0.7)
    while not genCorr:
        print("\nThe Player's gender is...\
            \n1 = boy (default)\
            \n2 = girl\
            \n3 = nonbinary")
        time.sleep(1.2)
        gender = input("Your answer: ")
        
        if gender == "1":
            player.gender = "Boy"
            time.sleep(0.7)
            print("\nConfirmed. The Player is a boy.")
            time.sleep(0.5)
            genCorr = confirmation()
        elif gender == "2":
            player.gender = "Girl"
            time.sleep(0.7)
            print("\nConfirmed. The Player is a girl.")
            time.sleep(0.5)
            genCorr = confirmation()
        elif gender == "3":
            player.gender = "Nonbinary"
            time.sleep(0.7)
            print("\nConfirmed. The Player is nonbinary.")
            time.sleep(0.5)
            genCorr = confirmation()
        else:
            miniPause()
            print("Error: Please enter an option from the list provided.")
        #time.sleep(0.5)
        #genCorr = confirmation()       

    time.sleep(0.7)
    print("\n------\nNext, let's enter the Player's pronouns.\n")

    correct = False
    """
    While loop for choosing the Player's pronouns (all 3 sets...)
    """
    while not correct:
        prn1Tb = None
        prn2Tb = None
        pvTb = None
        fcpTb = None

        time.sleep(0.7)
        print("The Player's default pronouns are he/him/his.\
            \nThe Player's default pronouns while wearing the Gerudo Set are she/her/hers.")
        time.sleep(1.5)
        defPrns = input("Would you like to customize the Player's pronouns? Y/N: ")
        
        if defPrns.lower() == "n" or defPrns.lower() == "no":

            player.numPrns = 1
            
            player.set_player_prns(player.prns1)
            player.set_vai_prns()
            
            time.sleep(0.5)
            # Review inputted information with the User in a Table.
            print("\nThe Player's default pronouns—with and without the Gerudo Set—are shown below:")

            prn1Tb = PrettyTable(["Type of Pronoun", "Your Input (Default)", "Your Input (Gerudo Set)"])
            
            prn1Tb.add_row(["Subjective", player.prns1["sub"], player.PV["sub"]])
            prn1Tb.add_row(["Objective", player.prns1["obj"], player.PV["obj"]])
            prn1Tb.add_row(["Possessive Determiner", player.prns1["pd"], player.PV["pd"]])
            prn1Tb.add_row(["Possessive Pronoun", player.prns1["pp"], player.PV["pp"]])
            prn1Tb.add_row(["Reflexive", player.prns1["ref"], player.PV["ref"]])
            prn1Tb.add_row(["Singular or Plural", "Singular", "Singular"])

            time.sleep(0.5)
            print(prn1Tb)

            time.sleep(1)
            correct = confirmation()

        elif defPrns.lower() == "y" or defPrns.lower() == "yes":
            time.sleep(0.5)
            print("\nYou have chosen to customize the Player's pronouns.")
            time.sleep(0.7)
            print("First, let's enter the Player's pronouns while wearing non-Gerudo Set clothing.\n")
            firstCorr = False # variable for confirming *first* pronoun set is *corr*ect

            """
            While loop for choosing the Player's first pronoun set
            """
            while not firstCorr:
                while True: # Prompt the user for the Player's subjective pronoun.
                    time.sleep(0.7)
                    print("Please enter the Player's subjective pronoun (1-4 characters).\
                        \nExamples: he (default), she, they\
                        \nExample sentence: *He* takes a long nap.")
                    time.sleep(1.6)
                    sub = input("Your answer: ")

                    if len(sub) < 1:
                        miniPause()
                        print("Error: Please enter at least 1 letter.\n")
                    elif len(sub) > 4:
                        miniPause()
                        print("Error: Please enter no more than 4 letters.\n")
                    elif alpha.match(sub) == None:
                        miniPause()
                        print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                    else:
                        print()
                        break

                while True: # Prompt the user for the Player's objective pronoun.
                    time.sleep(0.7)
                    print("Please enter the Player's objective pronoun (1-4 characters).\
                        \nExamples: him (default), her, them\
                        \nExample sentence: I give the ladle to *him.*")
                    time.sleep(1.6)
                    obj = input("Your answer: ")
                    if len(obj) < 1:
                        miniPause()
                        print("Error: Please enter at least 1 letter.\n")
                    elif len(obj) > 4:
                        miniPause()
                        print("Error: Please enter no more than 4 letters.")
                    elif alpha.match(obj) == None:
                        miniPause()
                        print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                    else:
                        print()
                        break

                while True: # Prompt the user for the Player's possessive determiner.
                    time.sleep(0.7)
                    print("Please enter the Player's possessive determiner (1-5 characters).\
                        \nExamples: his (default), her, their\
                        \nExample sentence: *His* hair is pink.")
                    time.sleep(1.6)
                    pd = input("Your answer: ")

                    if len(pd) < 1:
                        miniPause()
                        print("Error: Please enter at least 1 letter.\n")
                    elif len(pd) > 5:
                        miniPause()
                        print("Error: Please enter no more than 5 letters.")
                    elif alpha.match(pd) == None:
                        miniPause()
                        print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                    else:
                        print()
                        break
                
                while True: # Prompt the user for the Player's possessive pronoun.
                    time.sleep(0.7)
                    print("Please enter the Player's possessive pronoun (1-6 characters).\
                        \nExamples: his (default), hers, theirs\
                        \nExample sentence: The Hateno house is *his.*")
                    time.sleep(1.6)
                    pp = input("Your answer: ")
                    
                    if len(pp) < 1:
                        miniPause()
                        print("Error: Please enter at least 1 letter.\n")
                    elif len(pp) > 6:
                        miniPause()
                        print("Error: Please enter no more than 6 letters.")
                        
                    elif alpha.match(pp) == None:
                        miniPause()
                        print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                    else:
                        print()
                        break

                while True: # Prompt the user for the Player's reflexive pronoun.
                    time.sleep(0.7)
                    print("Please enter the Player's reflexive pronoun (1-8 characters).\
                        \nExamples: himself (default), herself, themself\
                        \nExample sentence: The hero cooks soup for *himself.*")
                    time.sleep(1.6)
                    ref = input("Your answer: ")
                    if len(ref) < 1:
                        miniPause()
                        print("Error: Please enter at least 1 letter.\n")
                    elif len(ref) > 8:
                        miniPause()
                        print("Error: Please enter no more than 8 letters.")
                    elif alpha.match(ref) == None:
                        miniPause()
                        print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                    else:
                        print()
                        break
                
                # subCap is needed for the example sentences below
                subCap = capitalize_first_let(sub)
                time.sleep(0.7)
                print("Please choose the group of sentences that feels most natural\
                        \nwith the Player's pronouns.\
                        \n1 = " + subCap + " takes the sword. " + subCap + " is Hyrule's last hope. (singular)\
                        \n2 = " + subCap + " take the sword. " + subCap + " are Hyrule's last hope. (plural)")
                
                while True: # Prompt the user to indicate whether the Player's pronouns are singular or plural.
                    time.sleep(1.7)     
                    sp = input("Your answer: ")

                    if sp != "1" and sp != "2":
                        miniPause()
                        print("Error: Please enter an option from the list provided.\n")
                    else:
                        break
                
                prn1Tb = PrettyTable(["Type of Pronoun", "Your Input"])
                prn1Tb.add_row(["Subjective", sub.lower()])
                prn1Tb.add_row(["Objective", obj.lower()])
                prn1Tb.add_row(["Possessive Determiner", pd.lower()])
                prn1Tb.add_row(["Possessive Pronoun", pp.lower()])
                prn1Tb.add_row(["Reflexive", ref.lower()])
                
                if sp == "1":
                    prn1Tb.add_row(["Singular or Plural", "Singular"])
                else:
                    prn1Tb.add_row(["Singular or Plural", "Plural"])

                time.sleep(0.7)
                print("\nThank you. These are the Player's pronouns while wearing non-Gerudo Set clothing:")
                time.sleep(0.5)
                print(prn1Tb)
                time.sleep(1.6)
                firstCorr = confirmation()
                                
            player.set_player_prns(player.prns1, sub, obj, pd, pp, ref, sp)

            """
            While loop for choosing the Player's second pronoun set
            """
            time.sleep(0.5)
            print("Next, you have the option to enter a second set of pronouns\
                \nfor the Player while wearing non-Gerudo Set clothing.\n")

            secondCorr = False
            
            while not secondCorr:
                time.sleep(1)
                second = input("Would you like to enter a second set of pronouns for the Player? Y/N: ")
                if second.lower() == "y" or second.lower() == "yes":
                    player.numPrns = 2

                    while True: # Prompt the user for the Player's subjective pronoun.
                        time.sleep(0.7)
                        print("Please enter the Player's subjective pronoun (1-4 characters).\
                            \nExamples: he (default), she, they\
                            \nExample sentence: *He* takes a long nap.")
                        time.sleep(1.6)
                        sub2 = input("Your answer: ")
                        if len(sub2) < 1:
                            miniPause()
                            print("Error: Please enter at least 1 letter.\n")
                        elif len(sub2) > 4:
                            miniPause()
                            print("Error: Please enter no more than 4 letters.")
                        elif alpha.match(sub2) == None:
                            miniPause()
                            print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                        else:
                            print()
                            break

                    while True: # Prompt the user for the Player's objective pronoun.
                        time.sleep(0.7)
                        print("Please enter the Player's objective pronoun (1-4 characters).\
                            \nExamples: him (default), her, them\
                            \nExample sentence: I give the ladle to *him.*")
                        time.sleep(1.6)
                        obj2 = input("Your answer: ")
                        if len(obj2) < 1:
                            miniPause()
                            print("Error: Please enter at least 1 letter.\n")
                        elif len(obj2) > 4:
                            miniPause()
                            print("Error: Please enter no more than 4 letters.")
                        elif alpha.match(obj2) == None:
                            miniPause()
                            print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                        else:
                            print()
                            break

                    while True: # Prompt the user for the Player's possessive determiner.
                        time.sleep(0.7)
                        print("Please enter the Player's possessive determiner (1-5 characters).\
                            \nExamples: his (default), her, their\
                            \nExample sentence: *His* hair is pink.")
                        time.sleep(1.6)
                        pd2 = input("Your answer: ")
                        if len(pd2) < 1:
                            miniPause()
                            print("Error: Please enter at least 1 letter.\n")
                        elif len(pd2) > 5:
                            miniPause()
                            print("Error: Please enter no more than 5 letters.")
                        elif alpha.match(pd2) == None:
                            miniPause()
                            print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                        else:
                            print()
                            break
                    
                    while True: # Prompt the user for the Player's possessive pronoun.
                        time.sleep(0.7)
                        print("Please enter the Player's possessive pronoun (1-6 characters).\
                            \nExamples: his (default), hers, theirs\
                            \nExample sentence: The Hateno house is *his.*")
                        time.sleep(1.6)
                        pp2 = input("Your answer: ")
                        if len(pp2) < 1:
                            miniPause()
                            print("Error: Please enter at least 1 letter.\n")
                        elif len(pp2) > 6:
                            miniPause()
                            print("Error: Please enter no more than 6 letters.")
                        elif alpha.match(pp2) == None:
                            miniPause()
                            print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                        else:
                            print()
                            break

                    while True: # Prompt the user for the Player's reflexive pronoun.
                        time.sleep(0.7)
                        print("Please enter the Player's reflexive pronoun (1-8 characters).\
                            \nExamples: himself (default), herself, themself\
                            \nExample sentence: The hero cooks soup for *himself.*")
                        time.sleep(1.6)
                        ref2 = input("Your answer: ")
                        if len(ref2) < 1:
                            miniPause()
                            print("Error: Please enter at least 1 letter.\n")
                        elif len(ref2) > 8:
                            miniPause()
                            print("Error: Please enter no more than 8 letters.")
                        elif alpha.match(ref2) == None:
                            miniPause()
                            print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                        else:
                            print()
                            break
                    
                    # sub2Cap is needed for the example sentences below
                    sub2Cap = capitalize_first_let(sub2)
                    time.sleep(0.7)
                    print("Please choose the group of sentences that feels most natural\
                            \nwith the Player's pronouns.\
                            \n1 = " + sub2Cap + " takes the sword. " + sub2Cap + " is Hyrule's last hope. (singular)\
                            \n2 = " + sub2Cap + " take the sword. " + sub2Cap + " are Hyrule's last hope. (plural)")
                    
                    while True: # Prompt the user to indicate whether the Player's pronouns are singular or plural.
                        time.sleep(1.7)              
                        sp2 = input("Your answer: ")

                        if sp2 != "1" and sp2 != "2":
                            miniPause()
                            print("Error: Please enter an option from the list provided.\n")
                        else:
                            break
                    
                    prn2Tb = PrettyTable(["Type of Pronoun", "Your Input"])
                    prn2Tb.add_row(["Subjective", sub2.lower()])
                    prn2Tb.add_row(["Objective", obj2.lower()])
                    prn2Tb.add_row(["Possessive Determiner", pd2.lower()])
                    prn2Tb.add_row(["Possessive Pronoun", pp2.lower()])
                    prn2Tb.add_row(["Reflexive", ref2.lower()])
                    
                    if sp2 == "1":
                        prn2Tb.add_row(["Singular or Plural", "Singular"])
                    else:
                        prn2Tb.add_row(["Singular or Plural", "Plural"])

                    player.set_player_prns(player.prns2, sub2, obj2, pd2, pp2, ref2, sp2)

                    # Print a table showing the second set of Player pronouns
                    time.sleep(0.5)
                    print("\nThank you. This is the Player's second set of pronouns\
                        \nwhile wearing non-Gerudo Set clothing:")
                    time.sleep(0.5)
                    print(prn2Tb)
                    time.sleep(1.6)
                    secondCorr = confirmation()

                elif second.lower() == "n" or second.lower() == "no":
                    player.numPrns = 1
                    time.sleep(0.5)
                    print("If you proceed, the Player will have *one* primary set of pronouns\
                        \nwhile wearing normal clothing, just like in the default game.")
                    time.sleep(1)
                    secondCorr = confirmation()
                else:
                    miniPause()
                    print("Error: Please answer with either \"yes\" or \"no.\"")
            
            """
            While loop for choosing pronoun set percentages
            """
            if player.prns2["sub"] != "":
                time.sleep(0.7)
                print("By default, the Player uses he/him/his pronouns 100% of the time\
                    \nwhile wearing non-Gerudo Set clothing.")
                time.sleep(1.5)
                print("\nFrom your input, the Player's pronouns are %s and %s." % (player.prns1["bio"], player.prns2["bio"]))
                time.sleep(1)
                print("\nPlease enter a number between 1-99 for the %% of the time that the\
                    \nPlayer uses %s pronouns while wearing non-Gerudo Set clothing." % (player.prns1["bio"]))
                
                perCorr = False # *per*cent *Corr*ect
                while not perCorr:
                    time.sleep(1.5)
                    percent = input("Your answer (number from 1-99): ")

                    try:
                        perNum = float(percent)
                    except TypeError:
                        print("Error: Please enter a number.\n")
                    except ValueError:
                        print("Error: Please enter a number.\n")
                    else:
                        percent = round(perNum) # Round perNum to the nearest int.
                        if percent < 1:
                            miniPause()
                            print("Error: Number is too low.\n")
                        elif percent > 99:
                            miniPause()
                            print("Error: Number is too high.\n")
                        else:
                            time.sleep(0.7)
                            print("Confirmed.\
                                \nWhile the Player wears non-Gerudo Set clothing, the Player uses...\
                                \n%s pronouns %i%% of the time, and\
                                \n%s pronouns %i%% of the time." % (player.prns1["bio"], percent, player.prns2["bio"], 100-percent))
                            time.sleep(2)
                            perCorr = confirmation()

                player.prns1["percent"] = percent
                player.prns2["percent"] = 100-percent
                player.PV["percent"] = "N/A"

            """
            While loop for choosing the Player's Vai pronoun set
            """
            time.sleep(0.7)
            print("Lastly, let's enter the Player's pronouns while wearing the Gerudo Set.\n")
            vaiCorr = False
            while not vaiCorr:
                while True: # Prompt the user for the Player's subjective pronoun.
                    time.sleep(0.7)
                    print("Please enter the Player's subjective pronoun (1-4 characters).\
                        \nExamples: she (default), he, they\
                        \nExample sentence: \"She\" wins the Sand-Seal Race.")
                    time.sleep(1.6)
                    vSub = input("Your answer: ")
                    if len(vSub) < 1:
                        miniPause()
                        print("Error: Please enter at least 1 letter.\n")
                    elif len(vSub) > 4:
                        miniPause()
                        print("Error: Please enter no more than 4 letters.\n")
                    elif alpha.match(vSub) == None:
                        miniPause()
                        print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                    else:
                        print()
                        break

                while True: # Prompt the user for the Player's objective pronoun.
                    time.sleep(0.7)
                    print("Please enter the Player's objective pronoun (1-4 characters).\
                        \nExamples: her (default), him, them\
                        \nExample sentence: Riju gives the helm to \"her.\"")
                    time.sleep(1.6)
                    vObj = input("Your answer: ")
                    if len(vObj) < 1:
                        miniPause()
                        print("Error: Please enter at least 1 letter.\n")
                    elif len(vObj) > 4:
                        miniPause()
                        print("Error: Please enter no more than 4 letters.\n")
                    elif alpha.match(vObj) == None:
                        miniPause()
                        print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                    else:
                        print()
                        break

                while True: # Prompt the user for the Player's possessive determiner.
                    time.sleep(0.7)
                    print("Please enter the Player's possessive determiner (1-5 characters).\
                        \nExamples: her (default), his, their\
                        \nExample sentence: \"Her\" swordplay is electric.")
                    time.sleep(1.6)
                    vPd = input("Your answer: ")
                    if len(vPd) < 1:
                        miniPause()
                        print("Error: Please enter at least 1 letter.\n")
                    elif len(vPd) > 5:
                        miniPause()
                        print("Error: Please enter no more than 5 letters.\n")
                    elif alpha.match(vPd) == None:
                        miniPause()
                        print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                    else:
                        print()
                        break
                               
                
                vSubCap = capitalize_first_let(vSub)
                time.sleep(0.7)
                print("Please choose the group of sentences that feels most natural\
                        \nwith the Player's pronouns.\
                        \n1 = %s enters Gerudo Town. %s is the new Sand-Seal Race Champion. (singular)\
                        \n2 = %s enter Gerudo Town. %s are the new Sand-Seal Race Champion. (plural)" % (vSubCap, vSubCap, vSubCap, vSubCap))
                
                while True: # Prompt the user to indicate whether the Player's pronouns are singular or plural.
                    time.sleep(1.7)
                    vSp = input("Your answer: ")

                    if vSp != "1" and vSp != "2":
                        miniPause()
                        print("Error: Please enter an option from the list provided.\n")
                    else:
                        break
                
                pvTb = PrettyTable(["Type of Pronoun", "Your Input"])
                pvTb.add_row(["Subjective", vSub.lower()])
                pvTb.add_row(["Objective", vObj.lower()])
                pvTb.add_row(["Possessive Determiner", vPd.lower()])
                
                if vSp == "1":
                    pvTb.add_row(["Singular or Plural", "Singular"])
                else:
                    pvTb.add_row(["Singular or Plural", "Plural"])
                                
                # Don't need to show percentage seen here either, if just confirming w/ user that these 1st pronouns are correct.
                time.sleep(0.7)
                print("\nThank you. These are the Player's pronouns while wearing the Gerudo Set:")
                time.sleep(0.5)
                print(pvTb)
                time.sleep(1.6)
                vaiCorr = confirmation()

                if vaiCorr:
                    correct = True
            
            player.set_vai_prns(vSub, vObj, vPd, vSp)
        else:
            miniPause()
            print("Error: Please answer with either \"Yes\" or \"No.\"\n")

    player.PV["percent"] = "N/A"

    nameGen = PrettyTable(["Player Name/Gender", "Your Input"])
    nameGen.add_row(["Full Name", player.name])
    nameGen.add_row(["Nickname from a genius scientist great-\naunt turned six-year-old. Check it!", player.nameD])
    nameGen.add_row(["Nickname from a Zora childhood friend.", player.nameZ])
    nameGen.add_row(["Gender", player.gender])

    # *f*inal *c*heck *p*layer *T*a*b*le --> fcpTb
    if prn2Tb == None:
        fcpTb = PrettyTable(["Type of Pronoun", "Your Input (Default)", "Your Input (Gerudo Set)"])
        
        fcpTb.add_row(["Subjective", player.prns1["sub"], player.PV["sub"]])
        fcpTb.add_row(["Objective", player.prns1["obj"], player.PV["obj"]])
        fcpTb.add_row(["Possessive Determiner", player.prns1["pd"], player.PV["pd"]])
        fcpTb.add_row(["Possessive Pronoun", player.prns1["pp"], player.PV["pp"]])
        fcpTb.add_row(["Reflexive", player.prns1["ref"], player.PV["ref"]])
        fcpTb.add_row(["Singular or Plural", player.prns1["sp"], player.PV["sp"]]) #????
    else:
        fcpTb = PrettyTable(["Type of Pronoun", "Your Input (Default 1)", "Your Input (Default 2)", "Your Input (Gerudo Set)"])
        
        fcpTb.add_row(["Subjective", player.prns1["sub"], player.prns2["sub"], player.PV["sub"]])
        fcpTb.add_row(["Objective", player.prns1["obj"], player.prns2["obj"], player.PV["obj"]])
        fcpTb.add_row(["Possessive Determiner", player.prns1["pd"], player.prns2["pd"], player.PV["pd"]])
        fcpTb.add_row(["Possessive Pronoun", player.prns1["pp"], player.prns2["pp"], player.PV["pp"]])
        fcpTb.add_row(["Reflexive", player.prns1["ref"], player.prns2["ref"], player.PV["ref"]])

        fcpTb.add_row(["Singular or Plural", player.prns1["sp"], player.prns2["sp"], player.PV["sp"]])
        fcpTb.add_row(["% Used", str(player.prns1["percent"])+"%", str(player.prns2["percent"])+"%", player.PV["percent"]])
        
    time.sleep(0.7)
    print("\n------\nFinal check- Below are all entered attributes for the Player:\n")
    time.sleep(0.7)
    print(nameGen)
    time.sleep(1)
    print()
    print(fcpTb)
    time.sleep(1.5)
        
    if confirmation():
        if player.numPrns == 1:
            f = PrettyTable(["Pronoun Type", "Player Pronouns (Default)", "Player Pronouns (Gerudo Set)"])
            f.add_rows(
                [
                    ["Subjective", player.prns1["sub"], player.PV["sub"]],
                    ["Objective", player.prns1["obj"], player.PV["obj"]],
                    ["Possessive Determiner", player.prns1["pd"], player.PV["pd"]],
                    ["Possessive Pronoun", player.prns1["pp"], player.PV["pp"]],
                    ["Reflexive", player.prns1["ref"], player.PV["ref"]],
                    ["Singular or Plural", player.prns1["sp"], player.PV["sp"]]
                ]
            )
        else:
            f = PrettyTable(["Pronoun Type", "Player Pronouns (Default 1)", "Player Pronouns (Default 2)", "Player Pronouns (Gerudo Set)"])
            f.add_rows(
                [
                    ["Subjective", player.prns1["sub"], player.prns2["sub"], player.PV["sub"]],
                    ["Objective", player.prns1["obj"], player.prns2["obj"], player.PV["obj"]],
                    ["Possessive Determiner", player.prns1["pd"], player.prns2["pd"], player.PV["pd"]],
                    ["Possessive Pronoun", player.prns1["pp"], player.prns2["pp"], player.PV["pp"]],
                    ["Reflexive", player.prns1["ref"], player.prns2["ref"], player.PV["ref"]],
                    ["Singular or Plural", player.prns1["sp"], player.prns2["sp"], player.PV["sp"]],
                    ["% Used", str(player.prns1["percent"])+"%", str(player.prns2["percent"])+"%", player.PV["percent"]]
                ]
            )
        player.prns_Tb = f
        return player
    else:
        return None

# Prompt user for Keeper attributes here.
# Keep in mind that Keeper Gender options rely on the inputted Player Gender.
def keeperAttr(p):
    print("\nDistilling Keeper Attributes...\n======")
    time.sleep(0.7)
    print("\nPlease enter the Keeper's name and gender.")

    nameCorr = False # "correct"/"confirmation" variable specifically for picking the Player's Name
    """
    While loop for choosing the Keeper's Name
    """
    time.sleep(0.7)
    while not nameCorr:
        keeper = None
        print("\nThe Keeper's name is...\
            \n1 = Zelda (default)\
            \n2 = Link\
            \n3 = Custom")
        time.sleep(0.7)
        name = input("Your answer: ")
        
        # Ask for both name and gender here, since the Keeper has no nicknames.
        if name == "1":
            keeper = Keeper()
        elif name == "2":
            keeper = Keeper(name)
        elif name == "3":
            print("Name customization screen activated.")

            while True:
                print("Please enter a name for the Keeper (1-8 characters).")
                time.sleep(1.6)
                cName = input("Your answer: ")

                if len(cName) < 1:
                    miniPause()
                    print("Error: Please enter at least 1 letter.\n")
                elif len(cName) > 8:
                    miniPause()
                    print("Error: Please enter no more than 8 letters.\n")
                elif alpha.match(cName) == None:
                    miniPause()
                    print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                else:
                    keeper = Keeper(name, cName)
                    print()
                    break
        else:
            print("Error: Please enter an option from the list provided.")
        
        if keeper != None:
            time.sleep(0.5)
            print("Keeper Name confirmed.")
            time.sleep(0.5)
            print("\nInitiating Gender selection screen...")
            time.sleep(1)
            print("The Player's gender' is: " + p.gender)
            time.sleep(0.5)
            print("The available options for the Keeper's gender are as follows: ")
            time.sleep(0.5)
            if p.gender == "Boy":
                print("\n1 = Girl (default)\
                    \n2 = Boy\
                    \n3 = Nonbinary")
            elif p.gender == "Girl":
                print("\n1 = Girl (default)\
                    \n2 = Boy")
            elif p.gender == "Nonbinary":
                print("\n1 = Girl (default)\
                    \n2 = Nonbinary")
        
            genCorr = False # while loop variable for confirming Keeper gender
            while not genCorr:
                time.sleep(0.5)
                gender = input("Your answer: ")
                time.sleep(0.5)

                if p.gender == "Boy":
                    if gender == "1":
                        print("Keeper is a Girl.")
                        keeper.gender = "Girl"
                        genCorr = True
                    elif gender == "2":
                        print("Keeper is a Boy.")
                        keeper.gender = "Boy"
                        genCorr = True
                    elif gender == "3":
                        print("Keeper is Nonbinary.")
                        keeper.gender = "Nonbinary"
                        genCorr = True
                    else:
                        print("Error: Please enter an option from the list provided.")

                elif p.gender == "Girl":
                    if gender == "1":
                        print("Keeper is a Girl.")
                        keeper.gender = "Girl"
                        genCorr = True
                    elif gender == "2":
                        print("Keeper is a Boy.")
                        keeper.gender = "Boy"
                        genCorr = True
                    else:
                        print("Error: Please enter an option from the list provided.")
                        
                elif p.gender == "Nonbinary":
                    if gender == "1":
                        print("Keeper is a Girl.")
                        keeper.gender = "Girl"
                        genCorr = True
                    elif gender == "2":
                        print("Keeper is Nonbinary.")
                        keeper.gender = "Nonbinary"
                        genCorr = True
                    else:
                        print("Error: Please enter an option from the list provided.")

            nameGen = PrettyTable(["Keeper Attribute", "Your Input"])

            nameGen.add_row(["Name", keeper.name])
            nameGen.add_row(["Gender", keeper.gender])
            time.sleep(1)
            print("The Keeper Name and Gender are as follows:\n")
            print(nameGen)
            time.sleep(2)
            nameCorr = confirmation()

    # Below are the current gender options:
    #if p.gender == "Boy":
    #    print("Keeper Gender can be Girl [Template A], Boy [D], or Nonbinary [F].")
    #elif p.gender == "Girl":
    #    print("Keeper Gender can be Girl [B] or Boy [E].")
    #elif p.gender == "Nonbinary":
    #    print("Keeper Gender can be Girl [C] or Nonbinary [G].")

    correct = False
    """
    While loop for choosing the Keeper's pronouns (both sets)
    """
    while not correct:
        fcpTb = None
        kTb = None
        kTb_2 = None

        time.sleep(0.7)
        print("The Keeper's default pronouns are she/her.")
        time.sleep(1)
        
        defPrns = input("Would you like to customize the Keeper's pronouns? Y/N: ")
        
        if defPrns.lower() == "n" or defPrns.lower() == "no":
            keeper.numPrns = 1
            keeper.set_keeper_prns(keeper.prns1_2)
            
            time.sleep(0.5)
            print("\nThe Keeper's default pronouns are shown below:")

            prn1Tb_2 = PrettyTable(["Type of Pronoun", "Your Input (Default)"])

            prn1Tb_2.add_row(["Subjective", keeper.prns1_2["sub"][0]])
            prn1Tb_2.add_row(["Objective", keeper.prns1_2["obj"][0]])
            prn1Tb_2.add_row(["Possessive Determiner", keeper.prns1_2["pd"][0]])
            prn1Tb_2.add_row(["Reflexive", keeper.prns1_2["ref"][0]])
            prn1Tb_2.add_row(["Singular or Plural", keeper.prns1_2["sp"]])

            print(prn1Tb_2)
            kTb = prn1Tb_2
            
            time.sleep(1)
            correct = confirmation()

        elif defPrns.lower() == "y" or defPrns.lower() == "yes":

            time.sleep(0.5)
            print("\nYou have chosen to customize the Keeper's pronouns.")
            time.sleep(0.7)
            print("Let's enter the Keeper's pronouns.\n")
            
            while True:
                # Make the table
                kTb = PrettyTable(["Pronoun Type", "Your Input"])
                kp = []
                i = 0
                
                for k in keeper.prns1_2:                    
                    if i >= 4:
                        break
                    print(keeper.prns1_2[k][2])
                    time.sleep(0.7)
                    
                    while True:
                        x = input("Your answer: ")
                        if len(x) < 1:
                            miniPause()
                            print("Error: Please enter at least 1 letter.\n")
                        elif len(x) > keeper.prns1_2[k][1]:
                            miniPause()
                            print("Error: Please enter no more than %i letters.\n" % keeper.prns1_2[k][1])
                        elif alpha.match(x) == None:
                            miniPause()
                            print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                        else:
                            kp.append(x.lower())
                            print()
                            i+=1
                            break
                
                sub2Cap = capitalize_first_let(kp[0])
                time.sleep(0.7)
                print("Please choose the group of sentences that feels most natural\
                        \nwith the Keeper's pronouns.\
                        \n1 = " + sub2Cap + " bears the light. " + sub2Cap + " is Hyrule's Goddess-blood royal. (singular)\
                        \n2 = " + sub2Cap + " bear the light. " + sub2Cap + " are Hyrule's Goddess-blood royal. (plural)")
                    
                while True: # Prompt the user to indicate whether the Player's pronouns are singular or plural.
                    time.sleep(1.7)              
                    sp2 = input("Your answer: ")
                    
                    if sp2 != "1" and sp2 != "2":
                        miniPause()
                        print("Error: Please enter an option from the list provided.\n")
                    else:
                        keeper.set_keeper_prns(keeper.prns1_2, kp[0], kp[1], kp[2], kp[3], sp2)
                        break
                                
                kTb.add_row(["Subjective", keeper.prns1_2["sub"][0]])
                kTb.add_row(["Objective", keeper.prns1_2["obj"][0]])
                kTb.add_row(["Possessive Determiner", keeper.prns1_2["pd"][0]])
                kTb.add_row(["Reflexive", keeper.prns1_2["ref"][0]])
                kTb.add_row(["Singular or Plural", keeper.prns1_2["sp"]])
                
                print("The Keeper's pronouns are as follows:")
                print(kTb)
                if confirmation():                    
                    break                   

            """
            While loop for choosing the Keeper's second pronoun set
            """
            time.sleep(0.5)
            print("Next, you have the option to enter a second set of pronouns\
                \nfor the Keeper.\n")

            secondCorr = False
            
            while not secondCorr:
                time.sleep(1)
                second = input("Would you like to enter a second set of pronouns for the Keeper? Y/N: ")
                if second.lower() == "y" or second.lower() == "yes":
                    keeper.numPrns = 2

                    while True:
                        # Make the table
                        kTb_2 = PrettyTable(["Pronoun Type", "Your Input"])
                        kp = []
                        i = 0
                        
                        for k in keeper.prns2_2:                    
                            if i >= 4:
                                break
                            print(keeper.prns2_2[k][2])
                            
                            while True:
                                x = input("Your answer: ")
                                if len(x) < 1:
                                    miniPause()
                                    print("Error: Please enter at least 1 letter.\n")
                                elif len(x) > keeper.prns2_2[k][1]:
                                    miniPause()
                                    print("Error: Please enter no more than %i letters.\n" % keeper.prns2_2[k][1])
                                elif not alpha.match(x):
                                    miniPause()
                                    print("Error: Please only enter Latin alphabet letters, i.e., a-z.\n")
                                else:
                                    kp.append(x.lower())
                                    print()
                                    i+=1
                                    break
                        
                        sub2Cap = capitalize_first_let(kp[0])
                        time.sleep(0.7)
                        print("Please choose the group of sentences that feels most natural\
                                \nwith the Keeper's pronouns.\
                                \n1 = " + sub2Cap + " bears the light. " + sub2Cap + " is Hyrule's Goddess-blood royal. (singular)\
                                \n2 = " + sub2Cap + " bear the light. " + sub2Cap + " are Hyrule's Goddess-blood royal. (plural)")
                            
                        while True: # Prompt the user to indicate whether the Keeper's pronouns are singular or plural.
                            time.sleep(1.7)              
                            sp2 = input("Your answer: ")

                            if sp2 == "1":
                                keeper.set_keeper_prns(keeper.prns2_2, kp[0], kp[1], kp[2], kp[3])
                                break
                            elif sp2 == "2":
                                keeper.set_keeper_prns(keeper.prns2_2, kp[0], kp[1], kp[2], kp[3], sp2)
                                break
                            else:
                                miniPause()
                                print("Error: Please enter an option from the list provided.\n")
                                        
                        kTb_2.add_row(["Subjective", keeper.prns2_2["sub"][0]])
                        kTb_2.add_row(["Objective", keeper.prns2_2["obj"][0]])
                        kTb_2.add_row(["Possessive Determiner", keeper.prns2_2["pd"][0]])
                        kTb_2.add_row(["Reflexive", keeper.prns2_2["ref"][0]])
                        kTb_2.add_row(["Singular or Plural", keeper.prns2_2["sp"]])
                        
                        print(kTb_2)
                        
                        c = confirmation()
                        if c:
                            secondCorr = c
                            break

                elif second.lower() == "n" or second.lower() == "no":
                    keeper.numPrns = 1
                    time.sleep(0.5)
                    print("If you proceed, the Keeper will have *one* set of pronouns,\
                        \njust like in the default game.")
                    time.sleep(1)
                    secondCorr = confirmation()
                    correct = secondCorr
                else:
                    miniPause()
                    print("Error: Please answer with either \"yes\" or \"no.\"")
            
            """
            While loop for choosing pronoun set percentages
            """            
            if keeper.numPrns == 2:
                time.sleep(0.7)
                print("By default, the Keeper uses she/her pronouns 100% of the time.")
                time.sleep(1.5)
                print("\nFrom your input, the Keeper's pronouns are %s and %s." % (keeper.prns1_2["bio"], keeper.prns2_2["bio"]))
                time.sleep(1)
                print("\nPlease enter a number between 1-99 for the %% of the time that the\
                    \nKeeper uses %s pronouns." % (keeper.prns1_2["bio"]))
                print("Note: Your input will be rounded to the nearest integer.")
                
                perCorr = False # *per*cent *Corr*ect
                while not perCorr:
                    
                    time.sleep(1.5)
                    percent = input("Your answer (number from 1-99): ")

                    try:
                        perNum = float(percent)
                    except TypeError:
                        print("Error: Please enter a number.\n")
                    except ValueError:
                        print("Error: Please enter a number.\n")
                    else:
                        percent = round(perNum) # Round perNum to the nearest int.
                        if percent < 1:
                            miniPause()
                            print("Error: Number is too low.\n")
                        elif percent > 99:
                            miniPause()
                            print("Error: Number is too high.\n")
                        else:
                            
                            time.sleep(0.7)
                            print("Confirmed.\
                                \nWhile the Player wears non-Gerudo Set clothing, the Player uses...\
                                \n%s pronouns %i%% of the time, and\
                                \n%s pronouns %i%% of the time." % (keeper.prns1_2["bio"], percent, keeper.prns2_2["bio"], 100-percent))
                            time.sleep(2)
                            perCorr = confirmation()
                            correct = perCorr

                keeper.prns1_2["percent"] = percent
                keeper.prns2_2["percent"] = 100-percent                
            
        else:
            miniPause()
            print("Error: Please answer with either \"Yes\" or \"No.\"\n")

    # *f*inal *c*heck *p*layer *T*a*b*le --> fcpTb

    if keeper.numPrns == 1:
        fcpTb = kTb
    else:
        fcpTb = PrettyTable(["Type of Pronoun", "Your Input (Default 1)", "Your Input (Default 2)"])
        
        fcpTb.add_row(["Subjective", keeper.prns1_2["sub"][0], keeper.prns2_2["sub"][0]])
        fcpTb.add_row(["Objective", keeper.prns1_2["obj"][0], keeper.prns2_2["obj"][0]])
        fcpTb.add_row(["Possessive Determiner", keeper.prns1_2["pd"][0], keeper.prns2_2["pd"][0]])
        
        fcpTb.add_row(["Reflexive", keeper.prns1_2["ref"][0], keeper.prns2_2["ref"][0]])

        fcpTb.add_row(["Singular or Plural", keeper.prns1_2["sp"], keeper.prns2_2["sp"]])
        fcpTb.add_row(["% Used", str(keeper.prns1_2["percent"])+"%", str(keeper.prns2_2["percent"])+"%"])

    time.sleep(0.7)
    print("\n------\nFinal check- Below are all entered attributes for the Keeper:\n")
    time.sleep(0.7)
    print(nameGen)
    time.sleep(1)
    print()
    print(fcpTb)
    time.sleep(1.5)
        
    if confirmation():
        if keeper.numPrns == 1:
            f = PrettyTable(["Pronoun Type", "Keeper Pronouns"])
            f.add_rows(
                [
                    ["Subjective", keeper.prns1_2["sub"][0]],
                    ["Objective", keeper.prns1_2["obj"][0]],
                    ["Possessive Determiner", keeper.prns1_2["pd"][0]],
                    ["Reflexive", keeper.prns1_2["ref"][0]],
                    ["Singular or Plural", keeper.prns1_2["sp"]]
                ]
            )
        else:
            f = PrettyTable(["Pronoun Type", "Keeper Pronouns 1", "Keeper Pronouns 2"])
            f.add_rows(
                [
                    ["Subjective", keeper.prns1_2["sub"][0], keeper.prns2_2["sub"][0]],
                    ["Objective", keeper.prns1_2["obj"][0], keeper.prns2_2["obj"][0]],
                    ["Possessive Determiner", keeper.prns1_2["pd"][0], keeper.prns2_2["pd"][0]],
                    ["Reflexive", keeper.prns1_2["ref"][0], keeper.prns2_2["ref"][0]],
                    ["Singular\nor Plural", keeper.prns1_2["sp"], keeper.prns2_2["sp"]],
                    ["% Used", str(keeper.prns1_2["percent"])+"%", str(keeper.prns2_2["percent"])+"%"]
                ]
            )
        keeper.prns_Tb = f

        return keeper
    else:
        return None

def make_output_dir():

    if not os.path.isdir('output'):
        os.mkdir('output')
    if not os.path.isdir('output/ActorType'):
        os.mkdir('output/ActorType')
    if not os.path.isdir('output/DemoMsg'):
        os.mkdir('output/DemoMsg')
    if not os.path.isdir('output/EventFlowMsg'):
        os.mkdir('output/EventFlowMsg')
    if not os.path.isdir('output/LayoutMsg'):
        os.mkdir('output/LayoutMsg')
    if not os.path.isdir('output/QuestMsg'):
        os.mkdir('output/QuestMsg')
    if not os.path.isdir('output/ShoutMsg'):
        os.mkdir('output/ShoutMsg')
    if not os.path.isdir('output/StaticMsg'):
        os.mkdir('output/StaticMsg')
    if not os.path.isdir('output/Tips'):
        os.mkdir('output/Tips')

def replace_vars_02(p, k):

    path = 'templates/'
    template = ""

    if (p.default == "3" and len(p.name) > 5) or (k.default == "3" and len(k.name) > 5):
        path += '6-8/'
    else:
        path += '1-5/'

    if p.gender == "Boy" and k.gender == "Girl":
        print("Template A Extracted: Boy Player, Girl Keeper.\n")
        # depending on Gender choices, path now points to the correct template directory
        path += 'A'
        template = "studly"
    elif p.gender == "Girl" and k.gender == "Girl":
        print("Template B Extracted: Girl Player, Girl Keeper.\n")
        path += 'B'
        template = "sturdy"
    elif p.gender == "Nonbinary" and k.gender == "Girl":
        print("Template C Extracted: Nonbinary Player, Girl Keeper.\n")
        path += 'C'
        template = "sturdy"
    elif p.gender == "Boy" and k.gender == "Boy":
        print("Template D Extracted: Boy Player, Boy Keeper.\n")
        path += 'D'
        template = "studly"
    elif p.gender == "Girl" and k.gender == "Boy":
        print("Template E Extracted: Girl Player, Boy Keeper.\n")
        path += 'E'
        template = "sturdy"
    elif p.gender == "Boy" and k.gender == "Nonbinary":
        print("Template F Extracted: Boy Player, Nonbinary Keeper.\n")
        path += 'F'
        template = "studly"
    elif p.gender == "Nonbinary" and k.gender == "Nonbinary":
        print("Template G Extracted: Nonbinary Player, Nonbinary Keeper.\n")
        path += 'G'
        template = "sturdy"
    else:
        print("Error. No template available for this gender combination.")
    
    make_output_dir()

    num_Files = 0
    counters = []
    counter_ind = 0

    combo_num_p = 0
    combo_num_k = 0
    # Use this to get the number of instances of relevant variables
    # in p.replace_combo and k.replace_combo as appropriate
    for folder in os.listdir(path):
        counters.append(0)
        for f in os.listdir(path+'/'+folder):
            counters[counter_ind] += 1
            num_Files += 1

            file = open(path+'/'+folder+'/'+f, "r", encoding="utf-8")
            
            data = file.read()
            
            if p.numPrns == 2:
                for a in p.replace_combo:

                    # Also need to factor out "[PName"
                    # And "V]"
                    if "[PName" not in a and "V]" not in a:
                        combo_num_p += data.count(a)
                    
                    if ("[P.01Sub]" in a or "[P.01Sub^]" in a or "[P.01Sub^^]" in a) \
                        and (a != "[P.01Sub]") and (a != "[P.01Sub^]") and (a !="[P.01Sub^^]"):
                        
                        combo_num_p -= data.count(a)
                                
                # math to avoid double counting some of the variables
            
            if k.numPrns == 2:
                for b in k.replace_combo:
                    if "[KName" not in b:
                        combo_num_k += data.count(b)
                    
                    if ("[K.01Sub]" in b or "[K.01Sub^]" in b) \
                        and (b != "[K.01Sub]") and (b != "[K.01Sub^]"):
                        combo_num_k -= data.count(b)
                # math to avoid double counting some of the variables
        counter_ind += 1

    if p.numPrns == 2:
        perc_01 = p.prns1["percent"]
        perc_02 = p.prns2["percent"]

        if perc_01 <= perc_02:
            vars_01 = (perc_01 * combo_num_p)/100
            vars_01 = math.ceil(vars_01)
            vars_02 = combo_num_p - vars_01
            
        else:
            vars_02 = (perc_02 * combo_num_p)/100
            vars_02 = math.ceil(vars_02)
            vars_01 = combo_num_p - vars_02
        
        acct_p = [vars_01, vars_02]

    if k.numPrns == 2:
        perc_01_k = k.prns1_2["percent"]
        perc_02_k = k.prns2_2["percent"]
        
        if perc_01_k <= perc_02_k:
            vars_01_k = (perc_01_k * combo_num_k)/100
            vars_01_k = math.ceil(vars_01_k)
            vars_02_k = combo_num_k - vars_01_k
            
        else:
            vars_02_k = (perc_02_k * combo_num_k)/100
            vars_02_k = math.ceil(vars_02_k)
            vars_01_k = combo_num_k - vars_02_k
        
        acct_k = [vars_01_k, vars_02_k]

    counter_ind = 0

    for folder in os.listdir(path):
        
        for pb_i in tqdm(range(counters[counter_ind]), desc='Distilling '+folder+' files...', ascii=False, ncols = 75):
            
            with open('output/' + folder + '/' + os.listdir(path+'/'+folder)[pb_i], 'wb') as file:
                
                with open(path + '/' + folder + '/' + os.listdir(path+'/'+folder)[pb_i], "r", encoding="utf-8") as x:
                    
                    lines = x.readlines()  # Get a list of every line of the input msyt file

                    # Parse through each input file line.
                    j = ""
                    for i in lines:
                        j = i
                        for var in p.replace_names:
                            j = j.replace(var, p.replace_names[var])
                        for var2 in p.replace_PV:
                            j = j.replace(var2, p.replace_PV[var2])
                        
                        if p.numPrns == 1:
                            for var3 in p.replace_dict_1:
                                j = j.replace(var3, p.replace_dict_1[var3])
                        else:
                            for var3 in p.replace_combo:
                        
                                occur_num = j.count(var3)
                                i = 0
                                while i < occur_num:
                                    index = random.choice([0,1])
                                    
                                    if acct_p[index] <= 0:
                                        index -= 1
                                    j = j.replace(var3, p.replace_combo[var3][index], 1)
                                    acct_p[index] -= 1
                                    i += 1
                        
                        j = j.replace("[KName]", k.name)


                        if k.numPrns == 1:
                            for var4 in k.replace_dict_1:
                                j = j.replace(var4, k.replace_dict_1[var4])
                        else:
                            for var4 in k.replace_combo:

                                occur_num = j.count(var4)
                                i = 0
                                while i < occur_num:
                                    index = random.choice([0,1])
                                    
                                    if acct_k[index] <= 0:
                                        index -= 1
                                    j = j.replace(var4, k.replace_combo[var4][index], 1)
                                    acct_k[index] -= 1
                                    i += 1
                        
                        file.write(j.encode())

        counter_ind += 1

    print()
    
    # Handle two unique EventFlowMsg files.
    # Assassin_006 dialogue includes words that share the same first letter with the Player Name.
    #
    # In HyruleWestHatago001, if the Player Name is any variation of "Zelda,"
    # the NPC remarks that the Player looks like the type of person who does research. :)
    if p.name == "Zelda":
        src1 = r'templates/other/Zelda/Npc_Assassin_006.msyt'
    elif p.name == "Link":
        src1 = r'templates/other/Link/Npc_Assassin_006.msyt'
    else:
        src1 = r'templates/other/Custom/Npc_Assassin_006.msyt' # contains variables to replace
    
    if p.name.lower() == "zelda":
        src2 = r'templates/other/Zelda/Npc_HyruleWestHatago001.msyt'
    else:
        src2 = r'templates/other/Link/Npc_HyruleWestHatago001.msyt'

    src3 = r''
    sources = [src1, src2, src3]   

    dst1 = r'output/EventFlowMsg/Npc_Assassin_006.msyt'
    dst2 = r'output/EventFlowMsg/Npc_HyruleWestHatago001.msyt'
    dst3 = r'output/EventFlowMsg/Npc_HatenoVillage031.msyt'

    dests = [dst1, dst2, dst3]

    print("Final cleanup...")

    if p.default == "3": #Custom name
        # Full selection of words that start with the same letter as the chosen name
        # but are slightly off
        full_set = []
        # 3 words that start with the same letter as the chosen name
        # but are slightly off
        three_set = []
        first_let = p.name[0].upper()
        replace_vars = ["[PName8-1]", "[PName8-2]", "[PName8-3]"]
        # Get the full set of words that start with the same
        # letter as the chosen name
        with open("dictionary.txt", "r", encoding="utf-8") as y:
            lines = y.readlines()

            for line in lines:
                if len(full_set) > 0 and line[0] != first_let:
                    break
                if line[0] == first_let:
                    full_set.append(line[:-1]) # a newline counts as one character        

        i = 0
        while i < 3:
            random_word = random.choice(full_set)

            if random_word.lower() != p.name.lower():
                if p.name[0] == random_word[0] and random_word not in three_set:
                    three_set.append(random_word)
                    i += 1
                elif p.name[0] != random_word[0] and random_word.lower() not in three_set:
                    three_set.append(random_word.lower())
                    i += 1


        #with open(dests[0], 'wb') as file:
        #    with open(sources[0], "r", encoding="utf-8") as x:
        #        lines = x.readlines()
        
        j = ""
        with open(dests[0], 'wb') as file:
            with open(sources[0], "r", encoding="utf-8") as x:
                lines = x.readlines()
                m = 0
                for line in lines:
                    m = 0
                    j = line
                    j = j.replace("[PName]", p.name)
                    j = j.replace("[PName1st]", p.name[0].upper())
                    while m < 3:
                    #for word in three_set:
                        j = j.replace(replace_vars[m], three_set[m])
                        m += 1
                    file.write(j.encode())
        #dst1 (also make sure this fits 8 characters -- just checked, it does!)

        #handle instances where name ends in "son"
        if len(p.name) >= 3 and p.name[-3:len(p.name)].lower() == "son":
            if template == "studly":
                src3 = r'templates/other/Custom/ADF/Npc_HatenoVillage031.msyt'
            else:
                src3 = r'templates/other/Custom/BCEG/Npc_HatenoVillage031.msyt'
            n = ""
            with open(dests[2], 'wb') as file:
                with open(src3, "r", encoding="utf-8") as x:
                    lines = x.readlines()
                    m = 0
                    for line in lines:
                        m = 0
                        n = line
                        n = n.replace("[PName]", p.name)                        
                        file.write(n.encode())
    else:
        shutil.copy(sources[0], dests[0])

    print("...")
    shutil.copy(sources[1], dests[1])

    """
    for cleanup in tqdm(range(2), desc='Final cleanup...', ascii=False, ncols=75):

        shutil.copy(sources[cleanup], dests[cleanup])
    """
    
    print("\nSuccess!")
    if p.numPrns == 1:
        print("Player: " + p.name + " | " + p.prns1["bio"] + " | " + p.gender)
    elif p.numPrns == 2:
        print("Player: " + p.name + " | " + p.prns1["bio"] + " " + str(p.prns1["percent"]) + "%, "\
            + p.prns2["bio"] + " " + str(p.prns2["percent"]) + "% | " + p.gender)
    
    if k.numPrns == 1:
        print("Keeper: " + k.name + " | " + k.prns1_2["bio"] + " | " + k.gender)
    elif k.numPrns == 2:
        print("Keeper: " + k.name + " | " + k.prns1_2["bio"] + " " + str(k.prns1_2["percent"]) + "%, "\
            + k.prns2_2["bio"] + " " + str(k.prns2_2["percent"]) + "% | " + k.gender)


# =======================================================
# Main
# =======================================================
def main():
    
    print("BotW Custom Character Text Editor")
    print("v1.0.0 authenticated.\n======")
        
    player = None
    keeper = None

    while player == None or keeper == None:
        
        while player == None:
            player = playerAttr()

        input("Player Attributes extracted. Press Enter to continue.")
        
        while keeper == None:
            keeper = keeperAttr(player)
            
        input("Keeper Attributes extracted. Press Enter to continue.")
        
        print()
        time.sleep(0.7)
        print("Final review of both Player and Keeper attributes:")
        time.sleep(0.7)
        final_nameGen = PrettyTable(["Name & Gender", "Player", "Keeper"])
        final_nameGen.add_rows(
            [
                ["Full Name", player.name, keeper.name],
                ["Nickname from a genius scientist great-\naunt turned six-year-old. Check it!", player.nameD, "N/A"],
                ["Nickname from a Zora childhood friend.", player.nameZ, "N/A"],
                ["Gender", player.gender, keeper.gender]
            ]
        )
        print(final_nameGen)
        print(player.prns_Tb)
        print(keeper.prns_Tb)
        time.sleep(4)
                
        confirm = input("Is this correct?\
            \nNote: If you enter \"No\", you may restart the\
            \nprocess of entering Player and Keeper attributes\
            \nfrom the beginning.\
            \nYour answer (Y/N): ")
        while True:
            time.sleep(0.5)

            if confirm.lower() == "y" or confirm.lower() == "yes":
                break
            elif confirm.lower() == "n" or confirm.lower() == "no":
                player = None
                keeper = None
                print("Restarting...")
                break
            else:
                miniPause()
                print("Error: Please answer with either \"yes\" or \"no.\"")
            confirm = input("Is this correct? Y/N: ")
    player.set_replace_dict()
    keeper.set_replace_dict()
    replace_vars_02(player, keeper)

def wait():
    print("Output generation complete. Press any key to continue.")
    m.getch()

main()
wait()