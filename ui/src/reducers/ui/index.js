import {
  TOGGLE_LOADING,
  SET_ERROR
} from '../../constants/actions/ui';

const initialState = {
  isLoading: false
};

const reduce = (state = initialState, action) => {
  switch (action.type) {
    case TOGGLE_LOADING: {
      return {
        ...state,
        isLoading: !state.isLoading
      };
    }
    case SET_ERROR: {
      return {
        ...state,
        error: action.payload
      };
    }
    default: {
      return state;
    }
  }
};

export default reduce;
