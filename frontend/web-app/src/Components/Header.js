import Typography from '@mui/material/Typography';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
const drawerWidth = 240;

export default function Header() {
    return (<AppBar
        position="fixed"
        sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px` }}
    >
        <Toolbar>
            <TipsAndUpdatesIcon sx={{ "marginRight": "30px" }} />
            <Typography variant="h6" noWrap component="div">
                Open Image Genius
            </Typography>
        </Toolbar>
    </AppBar>)
}
