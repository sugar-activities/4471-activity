# Copyright 2009 Simon Schampijer (based on his Hello World)
# Copyright 2011 Tony Forster
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""A text based dungeon."""

from textdungeon import starthere, readroomfile, compass, lookfloor
import gtk
import logging
import pango
from sugar.graphics import style
import simplejson

from gettext import gettext as _

from sugar.activity import activity
_NEW_TOOLBAR_SUPPORT = True

try:
    from sugar.graphics.toolbarbox import ToolbarBox
    from sugar.activity.widgets import ActivityButton
    from sugar.activity.widgets import ActivityToolbox
    from sugar.activity.widgets import TitleEntry
    from sugar.activity.widgets import StopButton
    from sugar.activity.widgets import ShareButton
    from sugar.activity.widgets import KeepButton
except:
    _NEW_TOOLBAR_SUPPORT = False
#    from toolbar import ReadToolbar, ViewToolbar

class TextdungeonActivity(activity.Activity):
    """TextdungeonActivity class as specified in activity.info"""

    def __init__(self, handle):
        """Set up the Textdungeon activity."""
        activity.Activity.__init__(self, handle)

        # we do not have collaboration features
        # make the share option insensitive
        self.max_participants = 1

        if _NEW_TOOLBAR_SUPPORT:
            # toolbar with the new toolbar redesign >= Sugar 0.88?
            toolbar_box = ToolbarBox()

            activity_button = ActivityButton(self)
            toolbar_box.toolbar.insert(activity_button, 0)
            activity_button.show()

            title_entry = TitleEntry(self)
            toolbar_box.toolbar.insert(title_entry, -1)
            title_entry.show()

            share_button = ShareButton(self)
            toolbar_box.toolbar.insert(share_button, -1)
            share_button.show()

            keep_button = KeepButton(self)
            toolbar_box.toolbar.insert(keep_button, -1)
            keep_button.show()
        
            separator = gtk.SeparatorToolItem()
            separator.props.draw = False
            separator.set_expand(True)
            toolbar_box.toolbar.insert(separator, -1)
            separator.show()

            stop_button = StopButton(self)
            toolbar_box.toolbar.insert(stop_button, -1)
            stop_button.show()

            self.set_toolbar_box(toolbar_box)
            toolbar_box.show()

        else:
            toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(toolbox)
            toolbox.show()

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_NEVER,
            gtk.POLICY_AUTOMATIC)
        self.scrolled_window.props.shadow_type = \
            gtk.SHADOW_NONE
        self.textview = gtk.TextView()
        self.textview.set_editable(True)
        self.textview.set_cursor_visible(True)
        self.textview.set_wrap_mode(True)
        self.textview.connect("key_press_event",
            self.keypress_cb)

        self.scrolled_window.add(self.textview)
        self.set_canvas(self.scrolled_window)
        self.textview.show()
        self.scrolled_window.show()
        self.textview.grab_focus()
        self.font_desc = pango.FontDescription("sans %d" %
            style.zoom(8))
        self.textview.modify_font(self.font_desc)
#        self.stringthing=""

        self.loc =[0, 0]
        self.direction =0
        self.roomdata  =[]
        self.items=[]
        self.doors=[]
        self.inventory=[]
        self.keyboardentrystring=''
        self.filecontents=''
        self.printtobuf( 'Press h for help')
        self.printtobuf( 'Use a text editor such as the Write Activity to edit this dungeon, create new ones or reset a dungeon\n')
        self.printtobuf( 'You are in a dimly lit cavern ' + 'facing '+ compass(self.direction))
        if handle.object_id==None:
            readroomfile(self)                  #load the default room 
#        self.printtobuf( 'On the floor is'+ str(lookfloor(self.loc, self.items))+'\n\n')


    def printtobuf(self, addtext):
        self.printtobufnonewline('\n')
        self.printtobufnonewline(addtext)
#        textbuffer = self.textview.get_buffer()
#        itera=textbuffer.get_end_iter()
#        endmark=textbuffer.create_mark(None, itera)
#        self.textview.scroll_mark_onscreen(endmark)


    def printtobufnonewline(self, addtext):
        textbuffer = self.textview.get_buffer()
#        self.stringthing+=addtext
#        textbuffer.set_text(self.stringthing)
#        self.textview.set_buffer(textbuffer)
        textbuffer.insert_at_cursor(addtext)
        itera=textbuffer.get_end_iter()
#        self.textview.scroll_to_iter(itera,0)
        endmark=textbuffer.create_mark(None, itera)
        self.textview.scroll_mark_onscreen(endmark)

    def keypress_cb(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
#        print keyname
        if keyname == 'Return':
            starthere(self,self.keyboardentrystring) 
            self.keyboardentrystring=''
            self.printtobuf ('\n')
        elif keyname == 'space':
            self.keyboardentrystring +=' ' 
            self.printtobufnonewline (' ')  
        elif keyname == 'BackSpace':
            self.keyboardentrystring =self.keyboardentrystring[:-1]
            self.printtobuf(self.keyboardentrystring) 
        else:
            self.keyboardentrystring +=keyname 
            self.printtobufnonewline (keyname)  
        return True


    def read_file(self, file_path):
        print file_path
        readroomfile(self,file_path)
                
    def write_file(self, file_path):
        ''' Write the project to the Journal. '''
#        _logger.debug('Write file: %s' % file_path)
        self.metadata['mime_type'] = 'text/plain'
        fd = open(file_path, 'w')
        text = self.filecontents + '<l,' +str(self.loc[0]) +',' + str(self.loc[1]) + '>\n' 
        text = text + '<i'
        for x in self.inventory:
            text=text+ ',' + x
        text=text+'>\n' 
        text=text+ '<u'
        for i in self.items:
            text=text+ ',' +str(i[0])+',' +str(i[1])+',' +i[2]
        text=text+'>\n' 
        text = text +'<end>'
        fd.write(text)
        fd.close()



