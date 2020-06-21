# %%
from striplog import Striplog

import json
from pprint import pprint
# %%
surface_picks = {"Montara Formation": 4620, "Plover Formation (Top Reservoir)": 4798.4, "base": 5000}

# %%
def surface_pick_dict_to_striplog(surface_picks):
    """
    Generate a striplog object from a dictionary of surface picks:
        eg {"top1": depth, "top2": depth}
    """
    csv_text = '\n'.join([f'{k},{v}' for k, v in surface_picks.items()])
    csv_text = "Comp Formation, Depth\n" + csv_text
    return Striplog.from_csv(text=csv_text)

# We can now go back and forth from json to striplog
# %%
s = surface_pick_dict_to_striplog(surface_picks)
j = json.dumps(s.to_csv())

# %%
Striplog.from_csv(text=json.loads(j))

# %%
text = "Top,Base,Component\r\n4620.0,4798.4,Montara Formation\r\n4798.4,4799.4,Plover Formation (Top Reservoir)\r\n"
Striplog.from_csv(text=text)

# %%
