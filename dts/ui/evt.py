"""
The ``dts.ui.evt`` module holds event handlers that work across the GUI. These expand the wxPython events framework to include DTS GUI specific notifications.

List of available events:

- TabCloseRequestedEvent, EVT_TAB_CLOSE_REQUESTED
- ValueUpdatedEvent, EVT_VALUE_UPDATED
- ColormapChangedEvent, EVT_COLORMAP_CHANGED
- ColormapAdjustedEvent, EVT_COLORMAP_ADJUSTED
- ChannelChangedEvent, EVT_CHANNEL_CHANGED
- ChannelImportedEvent, EVT_CHANNEL_IMPORTED
- PlotUpdatedEvent, EVT_PLOT_UPDATED
- MapUpdatedEvent, EVT_MAP_UPDATED
- OffsetSetEvent, EVT_OFFSET_SET
- SubsetSelectedEvent, EVT_SUBSET_SELECTED
- SubsetEditedEvent, EVT_SUBSET_EDITED
- SubsetDeletedEvent, EVT_SUBSET_DELETED
- DateFormatSetEvent, EVT_DATE_FORMAT_SET
- TooltipMovedEvent, EVT_TOOLTIP_MOVED
- DebugModeChangedEvent, EVT_DEBUG_MODE_CHANGED
- GeodataImportedEvent, EVT_GEODATA_IMPORTED


"""
import wx
import wx.lib.newevent

TestEvent, EVT_TEST_EVENT = wx.lib.newevent.NewEvent()
TestCommandEvent, EVT_TEST_COMMAND_EVENT = wx.lib.newevent.NewCommandEvent()


class _test(object):
    """This class can be subclassed to provide a testing framework for implementing and catching test events."""
    def fire_command_event(self):
        event = TestCommandEvent(-1, attr1="hello")
        #post the event
        wx.PostEvent(self, event)
        print "Test command event fired from "+self.GetName()

    def fire_test_event(self):
        event = TestEvent()
        #post the event
        wx.PostEvent(self, event)
        print "Test event fired from "+self.GetName()

    def catch_test_event(self):
        """Catches the test event in whatever object this function is set in, and prints the result. Useful for debugging purposes."""
        self.Bind(EVT_TEST_COMMAND_EVENT, self._cmd_test)
        self.Bind(EVT_TEST_EVENT, self._evt_test)

    def _cmd_test(self, evt):
        print "Command event caught in: "+self.GetName()
        evt.Skip()

    def _evt_test(self, evt):
        print "Event caught in: "+self.GetName()
        evt.Skip()

# Events


TabCloseRequestedEvent, EVT_TAB_CLOSE_REQUESTED = wx.lib.newevent.NewEvent()

ValueUpdatedEvent, EVT_VALUE_UPDATED = wx.lib.newevent.NewCommandEvent()

# Command Events

ColormapChangedEvent, EVT_COLORMAP_CHANGED = wx.lib.newevent.NewCommandEvent()
ColormapAdjustedEvent, EVT_COLORMAP_ADJUSTED = wx.lib.newevent.NewCommandEvent()
ChannelChangedEvent, EVT_CHANNEL_CHANGED = wx.lib.newevent.NewCommandEvent()

ChannelImportedEvent, EVT_CHANNEL_IMPORTED = wx.lib.newevent.NewCommandEvent()

PlotUpdatedEvent, EVT_PLOT_UPDATED = wx.lib.newevent.NewCommandEvent()
MapUpdatedEvent, EVT_MAP_UPDATED = wx.lib.newevent.NewCommandEvent()

OffsetSetEvent, EVT_OFFSET_SET = wx.lib.newevent.NewCommandEvent()

SubsetSelectedEvent, EVT_SUBSET_SELECTED = wx.lib.newevent.NewCommandEvent()
SubsetEditedEvent, EVT_SUBSET_EDITED = wx.lib.newevent.NewCommandEvent()
SubsetDeletedEvent, EVT_SUBSET_DELETED = wx.lib.newevent.NewCommandEvent()

DateFormatSetEvent, EVT_DATE_FORMAT_SET = wx.lib.newevent.NewCommandEvent()

TooltipMovedEvent, EVT_TOOLTIP_MOVED = wx.lib.newevent.NewCommandEvent()

DebugModeChangedEvent, EVT_DEBUG_MODE_CHANGED = wx.lib.newevent.NewCommandEvent()

GeodataImportedEvent, EVT_GEODATA_IMPORTED = wx.lib.newevent.NewCommandEvent()
