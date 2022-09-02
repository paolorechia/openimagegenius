import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ChatBubbleOutlineTwoToneIcon from '@mui/icons-material/ChatBubbleOutlineTwoTone';
import ImageTwoToneIcon from '@mui/icons-material/ImageTwoTone';
export default function SideMenu() {
    return (
        <List>
            {['Prompt', 'Created'].map((text, index) => (
                <ListItem key={text} disablePadding>
                    <ListItemButton>
                        <ListItemIcon>
                            {index % 2 === 0 ? <ChatBubbleOutlineTwoToneIcon /> : <ImageTwoToneIcon />}
                        </ListItemIcon>
                        <ListItemText primary={text} />
                    </ListItemButton>
                </ListItem>
            ))}
        </List>
    )
}