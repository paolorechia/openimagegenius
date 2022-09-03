import Drawer from '@mui/material/Drawer';
import Toolbar from '@mui/material/Toolbar';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';

const drawerWidth = 300;

export default function RequestsMenu(props) {
    console.log("Requests props", props)
    return (
        <Drawer
            sx={{
                width: drawerWidth,
                flexShrink: 0,
                '& .MuiDrawer-paper': {
                    width: drawerWidth,
                    boxSizing: 'border-box',
                },
            }}
            variant="permanent"
            anchor="right"
        >
            <Toolbar />
            <Divider />
            <Typography variant="h6" noWrap component="div" sx={{ "padding": "30px" }}>
                Your requests
            </Typography>

            {
                props && props.websockets && props.websockets.state && props.websockets.state.requests
                    ? <List>
                        {
                            props.websockets.state.requests.map(request => {
                                return (

                                    <ListItem key={request.data.request_id} disablePadding>
                                        {request.data.request_id}
                                    </ListItem>
                                )
                            })
                        }
                    </List>
                    : 'no props'
            }
        </Drawer>
    )
}