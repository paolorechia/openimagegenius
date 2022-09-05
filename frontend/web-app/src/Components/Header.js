import Typography from '@mui/material/Typography';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import MenuIcon from '@mui/icons-material/Menu';
import { IconButton } from '@mui/material';

export default function Header(props) {
    console.log(props.isRequestsDrawerOpen)
    return (<AppBar
        sx={{ width: "100%"}}
    >
        <Toolbar
            sx={{ 
                "display": "flex",
                "justify-content": "space-between"
            }}>
            {
                props.isDrawerOpen
                    ? <TipsAndUpdatesIcon sx={{ "marginRight": "30px" }} />
                    : <IconButton
                        color="inherit"
                        aria-label="open drawer"
                        onClick={props.handleDrawerOpen}
                        edge="start"
                    >
                        <MenuIcon
                            sx={{ "marginRight": "26px" }}
                        />
                    </IconButton>
            }
            <Typography variant="h6" noWrap component="div">
                Open Image Genius
            </Typography>
            {
                props.isRequestsDrawerOpen
                    ? ""
                    : <IconButton
                        color="inherit"
                        aria-label="open drawer"
                        onClick={props.handleRequestDrawerOpen}
                        edge="start"
                    >
                        <MenuIcon
                            sx={{ "marginLeft": "26px" }}
                        />
                    </IconButton>
            }
        </Toolbar>
    </AppBar>)
}
