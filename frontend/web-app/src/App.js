import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import Divider from '@mui/material/Divider';

import Header from './Header';
import SideMenu from './SideMenu';
import NotificationMenu from './NotificationMenu';
import ImageDetailScreen from './ImageDetailScreen';
import PromptScreen from './PromptScreen';

const drawerWidth = 240;


function App() {
  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <Header />
      <SideMenu />
      <Box
        component="main"
        sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}
      >
        <Toolbar />
        <PromptScreen />
      </Box>
      <NotificationMenu />
    </Box>
  );
}

export default App;