import {
  EDIT_MODE_ON,
  RESET_EDIT_MODE,
  TOGGLE_AUTOPRECOMPUTE,
  OPEN_EDIT_PRIORITIES_MODE,
  TOGGLE_SHOW_LOSSES,
} from '../../constants/actions/layout';

const initialState = {
  editMode: {
    isEnabled: false,
    hasChanges: false,
    canSave: false,
    autoPrecompute: false
  },
  editPrioritiesMode: {
    isEnabled: false
  },
  lossesTab: {
    show: false
  }
};

const reduce = (state = initialState, action) => {
  switch (action.type) {
    case EDIT_MODE_ON: {
      return {
        ...state,
        editMode: {
          ...state.editMode,
          ...action.payload,
          isEnabled: true
        }
      };
    }
    case RESET_EDIT_MODE: {
      return {
        ...state,
        editMode: {
          ...state.editMode,
          isEnabled: false,
          editToken: null,
          extendTimeout: null
        },
        editPrioritiesMode: {
          ...state.editPrioritiesMode,
          isEnabled: false
        }
      };
    }
    case TOGGLE_AUTOPRECOMPUTE: {
      return {
        ...state,
        editMode: {
          ...state.editMode,
          autoPrecompute: !state.editMode.autoPrecompute
        }
      };
    }
    case OPEN_EDIT_PRIORITIES_MODE: {
      return {
        ...state,
        editPrioritiesMode: {
          ...state.editPrioritiesMode,
          isEnabled: true
        }
      };
    }
    case TOGGLE_SHOW_LOSSES: {
      return {
        ...state,
        lossesTab: {
          show: !state.lossesTab.show
        }
      };
    }
    default: {
      return state;
    }
  }
};

export default reduce;
