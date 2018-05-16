import { TOGGLE_SELECTION } from '../../constants/actions/data';

const initialState = {
  serverData: {},
  selectedDates: []
};

const reduce = (state = initialState, action) => {
  switch (action.type) {
    case TOGGLE_SELECTION: {
      const { key } = action;
      const keyIndex = state.selectedDates.indexOf(key);

      if (keyIndex >= 0) {
        return {
          ...state,
          selectedDates: [
            ...state.selectedDates.slice(0, keyIndex),
            ...state.selectedDates.slice(keyIndex + 1)
          ]
        };
      }
      return {
        ...state,
        selectedDates: [
          ...state.selectedDates,
          key
        ]
      };
    }
    default: {
      return state;
    }
  }
};

export default reduce;
