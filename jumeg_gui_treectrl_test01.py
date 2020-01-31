#!/usr/bin/env python3
# coding: utf-8


import os,sys,argparse

import wx
import wx.lib.agw.customtreectrl as CT
from wx.lib.agw.customtreectrl import CustomTreeCtrl

from jumeg_base_config import JuMEG_CONFIG_YAML_BASE
# from jumeg.gui.wxlib.utils.jumeg_gui_wxlib_utils_property_grid import JuMEG_wxPropertyGridPageBase,JuMEG_wxPropertyGridPageNotebookBase,JuMEG_wxPropertyGridSubProperty

import logging
from jumeg.base import jumeg_logger
logger = logging.getLogger('jumeg')

__version__="2019-11-22-001"


"""
#https://stackoverflow.com/questions/15751029/how-do-i-properly-use-check-boxes-with-wx-lib-agw-customtreectrl-customtreectrl

import wx, wx.lib.agw.customtreectrl

app = wx.App(False)

fr = wx.Frame(None)

myModule = wx.lib.agw.customtreectrl
myStyle = (myModule.TR_DEFAULT_STYLE|myModule.TR_MULTIPLE
           |myModule.TR_FULL_ROW_HIGHLIGHT|myModule.TR_AUTO_CHECK_CHILD
           |myModule.TR_AUTO_CHECK_PARENT|myModule.TR_AUTO_TOGGLE_CHILD)

tree = myModule.CustomTreeCtrl(fr, agwStyle=myStyle)
treeRoot = tree.AddRoot("PyRx Enzymes")
treeNodes =['Node A','Node B', 'Node C']
treeItems = ['1', '2', '3']
for i, _ in enumerate(treeNodes):
    iNode = tree.AppendItem(treeRoot, treeNodes[i], ct_type=1)
    for ii in treeItems:
        tree.AppendItem(iNode, "%s %s"%(treeNodes[i].replace('Node ',''), ii), ct_type=1)
tree.Expand(treeRoot)

fr.Show()

app.MainLoop()
"""

"""
https://wxpython.org/Phoenix/docs/html/wx.lib.agw.customtreectrl.CustomTreeCtrl.html

AppendItem
        parentId – an instance of GenericTreeItem representing the item’s parent;

        text (string) – the item text label;

        ct_type (integer) – the item type (see SetItemType for a list of valid item types);

        wnd – if not None, a non-toplevel window to show next to the item, any subclass of wx.Window;

        image (integer) – an index within the normal image list specifying the image to use for the item in unselected state;

        selImage (integer) – an index within the normal image list specifying the image to use for the item in selected state; if image > -1 and selImage is -1, the same image is used for both selected and unselected items;

        data (object) – associate the given Python object data with the item.

        on_the_right (bool) – True positions the window on the right of text, False on the left of text and overlapping the image.

"""

"""
ComboBox stuff used for later
text_size = len(max(l,key=len))
combo = wx.ComboBox(self, -1, choices=l, style=wx.CB_READONLY|wx.CB_DROPDOWN)
#--- https://wxpython.org/Phoenix/docs/html/wx.Control.html#wx.Control.GetSizeFromTe
sz = combo.GetSizeFromTextSize(combo.GetTextExtent("W" * text_size) )
combo.SetInitialSize(sz)
"""


class MyTreeCtrl(CustomTreeCtrl):
   def __init__(self,parent,**kwargs):
       style = (CT.TR_DEFAULT_STYLE|CT.TR_MULTIPLE
               |CT.TR_FULL_ROW_HIGHLIGHT|CT.TR_HAS_VARIABLE_ROW_HEIGHT
               |CT.TR_AUTO_CHECK_CHILD
               |CT.TR_AUTO_CHECK_PARENT|CT.TR_AUTO_TOGGLE_CHILD
               |CT.TR_ELLIPSIZE_LONG_ITEMS|CT.TR_TOOLTIP_ON_LONG_ITEMS
               |CT.TR_ALIGN_WINDOWS)
               #|CT.TR_ALIGN_WINDOWS_RIGHT)
       
       super().__init__(parent,agwStyle=style)
       
       self._wx_init(**kwargs)


   def _init_tree_ctrl(self,data=None):
     
       txt_size = 10
       keys = list(data.keys())
       keys.sort()
    
       for k in keys:
           v = data[k]
           logger.info("key: {} value. {} type: {} ".format(k,v,type(v)))
        
           #--- type bool
           if isinstance(v,(bool)):
               child = self.AppendItem(self.root,"{}".format(k),ct_type=1)
               self.SetItemBold(child,True)
               self.SetPyData(child,data[k])
        
           elif isinstance(v,(str)):
               style = wx.TE_LEFT
               ctrl = wx.TextCtrl(self,-1,style=style,value=v)
               sz = ctrl.GetSizeFromTextSize(ctrl.GetTextExtent("W" * txt_size))
               ctrl.SetInitialSize(sz)
            
               child = self.AppendItem(self.root,"{}".format(k),wnd=ctrl,ct_type=0)
               self.SetPyData(child,data[k])
        
           #--- type list => make TextCtrl + clickOn show List + add,delete like PropertyGrid
           elif isinstance(v,(list)):
            
               l = [str(x) for x in v]  # make list.items to str
               # style= wx.TE_MULTILINE|wx.TE_RIGHT
               style = wx.TE_LEFT
               ctrl = wx.TextCtrl(self,-1,style=style,value=",".join(l))
               sz = ctrl.GetSizeFromTextSize(ctrl.GetTextExtent("W" * txt_size))
               ctrl.SetInitialSize(sz)
            
               child = self.AppendItem(self.root,"{}".format(k),wnd=ctrl)
               self.SetPyData(child,data[k])
        
           elif isinstance(v,(int)):
               continue
        
           elif isinstance(v,(float)):
               continue
        
           elif isinstance(v,(dict)):
               #--- ToDo call recursive; do not expand only OnClick
               continue


   def _wx_init(self,**kwargs):
       data = kwargs.get("data",{})
       logger.info(data)
       self.root = self.AddRoot(kwargs.get("root","Tree Ctrl") )
       
       self._init_tree_ctrl(data=data)
       
       self.Expand(self.root)


class CtrlPanel(wx.Panel):
    def __init__(self,parent,**kwargs):
        super().__init__(parent)
        self._CfgTreeCtrl = None
        
        self._wx_init(**kwargs)
        self._ApplyLayout()
    
    @property
    def cfg(self): return self._CFG
    
    @property
    def ConfigTreeCtrl(self): return self._CfgTreeCtrl
    
    def _wx_init(self,**kwargs):
        self.SetBackgroundColour(wx.GREEN)
        #--- load cfg
        self._CFG = JuMEG_CONFIG_YAML_BASE(**kwargs)
        self._CFG.update(**kwargs)
       
       #--- init TreeCtrl
        root="noise_reducer"
        self._CfgTreeCtrl = MyTreeCtrl(self,root=root, data=self.cfg.GetDataDict(key=root) )
       
       #--- init show button
        self._bt_info  = wx.Button(self,label="Show Config",name="BT.INFO")
        self._bt_close = wx.Button(self,label="Close",name="BT.CLOSE")
        self.Bind(wx.EVT_BUTTON,self.ClickOnButton)
    
    def _ApplyLayout(self):
        LEA = wx.LEFT | wx.EXPAND | wx.ALL
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        #---
        st1 = wx.StaticLine(self)
        st1.SetBackgroundColour("GREY85")
        st2 = wx.StaticLine(self)
        st2.SetBackgroundColour("GREY80")
        
        vbox.Add(st1,0,LEA,1)
        if self.ConfigTreeCtrl:
           vbox.Add(self.ConfigTreeCtrl,1,LEA,1)
        vbox.Add(st2,0,LEA,1)
       #--- buttons
        hbox= wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self._bt_info,0,LEA,2)
        hbox.Add((0,0),1,LEA,2)
        hbox.Add(self._bt_close,0,LEA,2)
        vbox.Add(hbox,0,LEA,2)
        
        self.SetAutoLayout(True)
        self.SetSizer(vbox)
        self.Fit()
        self.Layout()
    
    def ClickOnButton(self,evt):
        obj = evt.GetEventObject()
        if obj.GetName() == "BT.INFO":
            self.cfg.info()
        else:
            evt.Skip()

class MainWindow(wx.Frame):
  def __init__(self, parent, title, **kwargs):
    wx.Frame.__init__(self, parent, -1,title=title)
    self._wx_init(**kwargs)
   
  def _update_from_kwargs(self,**kwargs):
      pass
  
  def _wx_init(self,**kwargs):
        w,h = wx.GetDisplaySize()
        self.SetSize(w/4.0,h/3.0)
        self.Center()
        
        self._update_from_kwargs(**kwargs)
      #--- init STB in a new CLS
        self._STB = self.CreateStatusBar()
        
        self._PNL = CtrlPanel(self,**kwargs)
        
        self.Bind(wx.EVT_BUTTON,self.ClickOnButton)
        self.Bind(wx.EVT_CLOSE,self.ClickOnClose)
      
  def ClickOnButton(self,evt):
      obj = evt.GetEventObject()
      if obj.GetName() == "BT.CLOSE":
        self.Close()

  def ClickOnClose(self,evt):
      #--- place to clean your stuff
      evt.Skip()
     
#---
def run(opt):
    if opt.debug:
        opt.verbose = True
        opt.debug = True
        opt.path = "./config/"
        opt.config = "test_config.yaml"
    
    app = wx.App()
    
    if opt.path:
        cfg = os.path.join((opt).path,opt.config)
    else:
        cfg = opt.config
    
    frame = MainWindow(None,'JuMEG Config',config=cfg,verbose=opt.verbose,debug=opt.debug)
    frame.Show()
    
    app.MainLoop()

#----
def get_args(argv):
    info_global = """
     JuMEG Config GUI Start Parameter

     ---> view time series data FIF file
      jumeg_cfg_gui01.py --config=test_config.yaml --path=./config -v

    """
    
    parser = argparse.ArgumentParser(info_global)
    
    parser.add_argument("-p","--path",help="config file path")
    parser.add_argument("-cfg","--config",help="config file name")
    
    parser.add_argument("-v","--verbose",action="store_true",help="verbose mode")
    parser.add_argument("-d","--debug",action="store_true",help="debug mode")
    
    #--- init flags
    # ck if flag is set in argv as True
    # problem can not switch on/off flag via cmd call
    opt = parser.parse_args()
    for g in parser._action_groups:
        for obj in g._group_actions:
            if str(type(obj)).endswith('_StoreTrueAction\'>'):
                if vars(opt).get(obj.dest):
                    opt.__dict__[obj.dest] = False
                    for flg in argv:
                        if flg in obj.option_strings:
                            opt.__dict__[obj.dest] = True
                            break
    
    return opt,parser


#=========================================================================================
#==== MAIN
#=========================================================================================
if __name__ == "__main__":
    opt,parser = get_args(sys.argv)
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(-1)
    
    jumeg_logger.setup_script_logging(name=sys.argv[0],opt=opt,logger=logger)
    
    run(opt)

