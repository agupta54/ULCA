const configs = {
  BASE_URL: "http://34.221.132.8:8080/",
  BASE_URL_AUTO: process.env.REACT_APP_APIGW_BASE_URL
    ? process.env.REACT_APP_APIGW_BASE_URL
    : "https://meity-auth.ulcacontrib.org",
  DEV_SALT: process.env.SALT
    ? process.env.SALT
    : "85U62e26b2aJ68dae8eQc188e0c8z8J9",
  BASE_DASHBOARD: "https://sangrah-dev-api.anuvaad.org",
  SOCKET_URL: "https://inference.vakyansh.in/",
};

export default configs;
