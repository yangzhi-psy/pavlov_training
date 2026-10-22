import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'code'))
"""Participant flow: source counts from public roster and manuscript allocation counts."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from pathlib import Path
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from shared import OUTPUT, inputs


def main():
    data, people = inputs()
    counts = data.groupby('group').participant_id.nunique().to_dict()
    assert counts == {'A':51,'B':47,'C':50}
    assert (people.group=='B').sum()==48
    flow = pd.DataFrame([
        ('Exp 1 randomized',107,'manuscript allocation'),('ADT allocated',54,'manuscript allocation'),
        ('LDT allocated',53,'manuscript allocation'),('ADT discontinued',3,'54 minus cognitive cohort'),
        ('LDT discontinued',5,'53 minus 48 roster completers'),
        ('LDT completers',48,'public participants'),('LDT completer missing cognitive data',1,'public participants'),
        ('ADT analyzed',51,'cognitive_long'),('LDT analyzed',47,'cognitive_long'),
        ('Exp 2 screened',57,'manuscript flow'),('Exp 2 screening excluded',7,'57 minus 50'),
        ('Exp 2 analyzed',50,'cognitive_long')],columns=['stage','n','source'])
    directory=OUTPUT/'Figure_1'; directory.mkdir(exist_ok=True)
    flow.to_csv(directory/'source_data.csv',index=False,lineterminator='\n')
    if Path(__file__).resolve().parent.name == 'code':
        (directory/'plot.py').write_text(
            "import sys\nfrom pathlib import Path\n"
            "sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'code'))\n"
            + Path(__file__).read_text(), newline='\n')
    (directory/'build.py').write_text(
        '"""Regenerate Figure 1 from public data and documented manuscript flow counts."""\n'
        'import sys\nfrom pathlib import Path\n'
        "sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'code'))\n"
        'from figure1 import main\nmain()\n', newline='\n')
    fig,ax=plt.subplots(figsize=(14,9));ax.set_xlim(0,14);ax.set_ylim(0,9);ax.axis('off')
    def box(x,y,width,height,label,color='white',edge='#333333'):
        ax.add_patch(FancyBboxPatch((x,y),width,height,boxstyle='round,pad=0.1',
                                    facecolor=color,edgecolor=edge,linewidth=1.2))
        ax.text(x+width/2,y+height/2,label,ha='center',va='center',fontsize=10,fontweight='bold')
    def arrow(x1,y1,x2,y2):
        ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=15,color='#333333'))
    green='#d8ead5';yellow='#fff2cb'
    box(.6,7.8,5, .8,'Experiment 1 (randomized)\nRecruited (n = 107)',green)
    box(8.4,7.8,5,.8,'Experiment 2 (non-randomized)\nControl cohort recruited (n = 57)',yellow)
    box(.3,6.2,2.8,.8,'Adaptive difficulty\nADT (n = 54)')
    box(3.8,6.2,2.8,.8,'Low difficulty\nLDT (n = 53)')
    arrow(2.5,7.8,1.7,7);arrow(3.5,7.8,5.2,7)
    box(.3,4.7,2.8,.7,'Discontinued (n = 3)')
    box(3.8,4.7,2.8,.7,'Discontinued (n = 5)')
    arrow(1.7,6.2,1.7,5.4);arrow(5.2,6.2,5.2,5.4)
    box(1.5,3.4,4,.7,'Completed training (n = 99)')
    arrow(3.5,4.7,3.5,4.1)
    box(3.9,2.35,2.8,.55,'No cognitive data (LDT, n = 1)')
    arrow(4.7,3.4,5.2,3)
    box(.1,1.25,2.8,.8,'Analyzed ADT (n = 51)',green)
    box(3.4,1.25,2.8,.8,'Analyzed LDT (n = 47)',green)
    arrow(2.4,3.4,1.5,2.05);arrow(3.5,3.4,4.8,2.05)
    box(9.1,6.2,3.7,.8,'Excluded at screening (n = 7)')
    arrow(10.9,7.8,10.9,7)
    box(9.1,4.2,3.7,.8,'Recreational gaming control (n = 50)')
    arrow(10.9,6.2,10.9,5)
    box(9.1,1.25,3.7,.8,'Analyzed control (n = 50)',yellow)
    arrow(10.9,4.2,10.9,2.05)
    box(.1,.15,6.1,.6,'Experiment 1: ADT (51) vs. LDT (47)',green)
    box(7,.15,6.2,.6,'Experiment 2: ADT (51) vs. control (50); matched (19 pairs)',yellow)
    arrow(3.2,1.25,3.2,.75);arrow(10.9,1.25,10.9,.75)
    fig.tight_layout();fig.savefig(directory/'Figure_1.png',dpi=200)
    fig.savefig(directory/'Figure_1.pdf',metadata={'CreationDate': datetime(2000,1,1)})
    plt.close(fig)


if __name__ == '__main__':
    main()
