import FindInPageIcon from '@material-ui/icons/FindInPage';
import { withStyles } from '@material-ui/core/styles';
import DatasetStyle from '../../../styles/Dataset';
import SearchRoundedIcon from '@material-ui/icons/SearchRounded';
import searchIcon from "../../../../assets/searchIcon.svg"
import {
    Typography
} from '@material-ui/core';
const SearchResult = (props) => {
    const { classes } = props;
    return (
        <div className={classes.searchResult}>
            <div>
                <img
                    src={searchIcon}
                    alt="Search Icon"
                />
                {/* <SearchRoundedIcon className={classes.FindInPageIcon} color="primary" /> */}
                <Typography color="primary" variant="h5">Your search result will appear here  </Typography>
            </div>
        </div>
    )
}

export default withStyles(DatasetStyle)(SearchResult);