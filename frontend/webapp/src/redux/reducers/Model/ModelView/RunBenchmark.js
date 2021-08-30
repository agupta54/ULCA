import C from "../../../actions/constants";

const initialState = {
  result: [],
};

const getBenchmarkDetails = () => {
  const result = {
    result: [
      {
        datasetName: "D1",
        domain: "Legal",
        description: "Lorem Ipsum",
      },
      {
        datasetName: "D2",
        domain: "Legal",
        description: "Lorem Ipsum",
      },
      {
        datasetName: "D3",
        domain: "Legal",
        description: "Lorem Ipsum",
      },
    ],
  };
  return result;
};

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case C.RUN_BENCHMARK:
      return {
        ...getBenchmarkDetails(),
      };
    default:
      return {
        ...state,
      };
  }
};

export default reducer;
