import { withStyles } from "@material-ui/core/styles";
import DatasetStyle from "../../../../styles/Dataset";
import { useHistory } from "react-router";
import InfoOutlinedIcon from "@material-ui/icons/InfoOutlined";
import UrlConfig from "../../../../../configs/internalurlmapping";
import HostedInferenceAPI from "../../../../../redux/actions/api/Model/ModelSearch/HostedInference";
import AudioRecord from "./VoiceRecorder";
import Spinner from "../../../../components/common/Spinner"
import {
  Grid,
  Typography,
  TextField,
  Button,
  CardContent,
  Card,
  CardActions,
} from "@material-ui/core";
import { useState } from "react";

const HostedInferASR = (props) => {
  const { classes, title, para, modelId, task } = props;
  const history = useHistory();
  const [url, setUrl] = useState("");
  const [apiCall, setApiCall] = useState(false);
  const [error, setError] = useState({ url: "" });
  const [snackbar, setSnackbarInfo] = useState({
    open: false,
    message: "",
    variant: "success",
  });
  const [translation, setTranslationState] = useState(false);
  const [target, setTarget] = useState("");
  const handleCompute = () => setTranslationState(true);
  // const url = UrlConfig.dataset
  const handleClose = () => {
    // setAnchorEl(null);
  };
  const validURL = (str) => {
    var pattern = new RegExp(
      "^((ft|htt)ps?:\\/\\/)?" + // protocol
        "((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|" + // domain name and extension
        "((\\d{1,3}\\.){3}\\d{1,3}))" + // OR ip (v4) address
        "(\\:\\d+)?" + // port
        "(\\/[-a-z\\d%@_.~+&:]*)*" + // path
        "(\\?[;&a-z\\d%@_.,~+&:=-]*)?" + // query string
        "(\\#[-a-z\\d_]*)?$",
      "i"
    ); // fragment locator
    return pattern.test(str);
  };
  const handleSubmit = (e) => {
    if (!validURL(url)) {
      setError({ ...error, url: "‘Invalid URL" });
    } else {
      handleApicall();
      setSnackbarInfo({
        ...snackbar,
        open: true,
        message: "Please wait while we process your request...",
        variant: "info",
      });
    }
  };
  const handleApicall = async () => {
    let apiObj = new HostedInferenceAPI(modelId, url, task);
    setApiCall(true)
    fetch(apiObj.apiEndPoint(), {
      method: "post",
      body: JSON.stringify(apiObj.getBody()),
      headers: apiObj.getHeaders().headers,
    })
      .then(async (response) => {
        const rsp_data = await response.json();
        setApiCall(false)
        if (!response.ok) {
          setSnackbarInfo({
            ...snackbar,
            open: true,
            message:
              "The model is not accessible currently. Please try again later",
            timeOut: 40000,
            variant: "error",
          });
        } else {
          if (rsp_data.hasOwnProperty("asr") && rsp_data.asr) {
            setTarget(rsp_data.asr.output[0].target);
            setTranslationState(true);
          }
        }
      })
      .catch((error) => {
        setApiCall(false)
        setSnackbarInfo({
          ...snackbar,
          open: true,
          message:
            "The model is not accessible currently. Please try again later",
          timeOut: 40000,
          variant: "error",
        });
      });
  };

  const handleSnackbarClose = () => {
    setSnackbarInfo({ ...snackbar, open: false });
  };

  return (
    <Grid container>

{apiCall && <Spinner />}
      {/* <Typography className={classes.hosted}>Hosted inference API {< InfoOutlinedIcon className={classes.buttonStyle} fontSize="small" color="disabled" />}</Typography> */}

      <Grid
        className={classes.gridCompute}
        item
        xl={5}
        lg={5}
        md={5}
        sm={5}
        xs={5}
      >
        <AudioRecord modelId = {modelId}/>
      </Grid>
      <Grid
        className={classes.gridCompute}
        item
        xl={6}
        lg={6}
        md={6}
        sm={6}
        xs={6}
      >
        <Card className={classes.asrCard}>
          <CardContent>
            <textarea
              disabled
              rows={6}
              value={target}
              className={classes.textArea}
            />
          </CardContent>
        </Card>
      </Grid>
      
      <Typography variant={"body1"}>Disclaimer : </Typography>
      
      <Typography variant={"caption"}>Transcription is best if you directly speak into the microphone and the performance might not be the same if you use it over a conference call.</Typography>
        
      <Grid
        className={classes.gridCompute}
        item
        xl={5}
        lg={5}
        md={5}
        sm={5}
        xs={5}
      >
        <Card className={classes.asrCard}>
          <CardContent>
              <Typography  variant={"caption"}>Max duration: 15 mins (If more, transcript of first 15 mins only will be given)</Typography>
            <TextField
            style={{marginTop:"15px",marginBottom:"10px"}}
              fullWidth
              color="primary"
              label="Paste the URL of the public repository"
              value={url}
              error={error.url ? true : false}
              helperText={error.url}
              onChange={(e) => {
                setUrl(e.target.value);
                setError({ ...error, url: false });
              }}
            />
          </CardContent>
          <CardActions
            style={{ justifyContent: "flex-end", paddingRight: "20px" }}
          >
            <Button
              color="primary"
              className={classes.computeBtn}
              variant="contained"
              size={"small"}
              onClick={handleSubmit}
            >
              Convert
            </Button>
          </CardActions>
        </Card>
      </Grid>
      <Grid
        className={classes.gridCompute}
        item
        xl={6}
        lg={6}
        md={6}
        sm={6}
        xs={6}
      >
      <Card className={classes.asrCard}>
        <CardContent>{target}</CardContent>
      </Card>
      </Grid>
    </Grid>
  );
};
export default withStyles(DatasetStyle)(HostedInferASR);
