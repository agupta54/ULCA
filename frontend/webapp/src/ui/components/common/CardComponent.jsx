import BlueCard from "../../../assets/card.svg";
import GreenCard from "../../../assets/card2.svg";
import Record from "../../../assets/record.svg";
import { Grid, Typography, withStyles } from "@material-ui/core";
import CommonStyles from "../../styles/Styles";
import {
  getLanguageName,
  getTaskName,
  FilterByDomain,
} from "../../../utils/getLabel";
import React, { Suspense } from "react";

const CardComponent = (props) => {
  const { value, classes } = props;

  const renderPublishedOn = (data) => {
    if (data.publishedOn)
      return (
        <Grid item>
          <Typography
            variant="caption"
            style={{ color: "#ffffff", opacity: "0.6" }}
            gutterBottom
          >
            Published On
          </Typography>
          <Typography variant="body2" style={{ color: "#ffffff" }}>
            {data.publishedOn.split(",")[0]}
          </Typography>
        </Grid>
      );
    return <></>;
  };

  const renderSubmitterName = (data) => {
    if (data.publishedOn)
      return (
        <Grid item xs={3} sm={3} md={3} lg={4} xl={4}>
          <Typography
            variant="caption"
            style={{ color: "#ffffff", opacity: "0.6" }}
            gutterBottom
          >
            Submitter
          </Typography>
          <Typography variant="body2" style={{ color: "#ffffff" }}>
            {data.submitter}
          </Typography>
        </Grid>
      );
    return (
      <Grid>
        <Typography
          variant="caption"
          style={{ color: "#ffffff", opacity: "0.6" }}
          gutterBottom
        >
          Submitter
        </Typography>
        <Typography variant="body2" style={{ color: "#ffffff" }}>
          {data.submitter}
        </Typography>
      </Grid>
    );
  };

  const renderDomain = (data) => {
    return (
      <Grid item xs={3} sm={3} md={3} lg={4} xl={4}>
        <Typography
          variant="caption"
          style={{ color: "#ffffff", opacity: "0.6" }}
          gutterBottom
        >
          Domain
        </Typography>
        <Typography variant="body2" style={{ color: "#ffffff" }}>
          {FilterByDomain([data.domain])[0].label}
        </Typography>
      </Grid>
    );
  };

  const renderSourceLanguage = (data) => {
    return (
      <Grid item xs={4} sm={4} md={4} lg={4} xl={4}>
        <Typography
          variant="caption"
          style={{ color: "#ffffff", opacity: "0.6" }}
          gutterBottom
        >
          {data.task === "translation" ? "Source" : "Language"}
        </Typography>
        <Typography variant="body2" style={{ color: "#ffffff" }}>
          {getLanguageName(data.source)}
        </Typography>
      </Grid>
    );
  };

  const renderTargetLanguage = (data) => {
    if (data.task === "translation")
      return (
        <Grid item xs={4} sm={4} md={4} lg={4} xl={4}>
          <Typography
            variant="caption"
            style={{ color: "#ffffff", opacity: "0.6" }}
            gutterBottom
          >
            Target
          </Typography>
          <Typography variant="body2" style={{ color: "#ffffff" }}>
            {getLanguageName(data.target)}
          </Typography>
        </Grid>
      );
    return <></>;
  };

  const renderLanguage = (data) => {
    return (
      <Grid className={classes.cardGrid} container>
        {renderSourceLanguage(data)}
        {renderTargetLanguage(data)}
      </Grid>
    );
  };

  const renderMetaData = (data) => {
    return (
      <Grid style={{ marginTop: "20px", color: "#ffffff" }} container>
        {renderDomain(data)}
        {renderSubmitterName(data)}
        {renderPublishedOn(data)}
      </Grid>
    );
  };

  const renderTaskName = (data) => {
    return (
      <Typography className={classes.typeTypo} variant="body2">
        {getTaskName(data.task)}
      </Typography>
    );
  };

  const renderModelName = (data) => {
    return (
      <Typography variant="h6" className={classes.modelname}>
        {data.modelName}
      </Typography>
    );
  };

  const renderModelInfo = (data) => {
    return (
      <div
        onClick={() => props.onClick(data)}
        style={{
          padding: "10px 20px",
          boxSizing: "border-box",
          cursor: "pointer",
        }}
      >
        {renderTaskName(data)}
        {renderModelName(data)}
        {renderLanguage(data)}
        {renderMetaData(data)}
      </div>
    );
  };

  const renderCardGrid = () => {
    const elemArr = value.filteredData.map((data, i) => {
      return (
        <Grid
          key={i}
          item
          xs={12}
          sm={6}
          md={5}
          lg={4}
          xl={4}
          className={i % 2 === 0 ? classes.card : classes.card2}
        >
          {renderModelInfo(data)}
        </Grid>
      );
    });
    return elemArr;
  };

  const renderCardComp = () => {
    if (value.filteredData.length)
      return (
        <Grid container spacing={2} className={classes.cardGrid}>
          {renderCardGrid()}
        </Grid>
      );

    return <div style={{ background: `url(${Record}) no-repeat` }}></div>;
  };

  return <>{renderCardComp()}</>;
};

export default withStyles(CommonStyles)(CardComponent);
