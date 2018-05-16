import { combineReducers } from 'redux';
import reduceReducers from 'reduce-reducers';
import toolbar from './toolbarReducer';
import data from './dataReducer';
import modal from './modalReducer';
import {
  UPDATE_LAYOUT_DATA,
  HANDLE_PRECOMPUTED_DATA,
  UPDATE_CELLS,
  SAVE_LAYOUT_PRIORITIES,
  CLOSE_EDIT_PRIORITIES_MODE
} from '../../constants/actions/layout';

const crossSliceReducer = (state, action) => {
  switch (action.type) {
    case UPDATE_LAYOUT_DATA: {
      return {
        ...state,
        toolbar: {
          ...state.toolbar,
          editMode: {
            ...state.toolbar.editMode,
            canSave: false,
            hasChanges: false
          }
        },
        data: {
          ...state.data,
          ...action.payload
        }
      };
    }
    case HANDLE_PRECOMPUTED_DATA: {
      return {
        ...state,
        toolbar: {
          ...state.toolbar,
          editMode: {
            ...state.toolbar.editMode,
            hasChanges: false,
            canSave: true
          }
        },
        data: {
          ...state.data,
          formattedData: action.formattedData,
          lossesData: action.lossesData
        }
      };
    }
    case UPDATE_CELLS: {
      return {
        ...state,
        toolbar: {
          ...state.toolbar,
          editMode: {
            ...state.toolbar.editMode,
            hasChanges: true,
            canSave: false
          }
        },
        data: {
          ...state.data,
          formattedData: action.newData
        }
      };
    }
    case SAVE_LAYOUT_PRIORITIES: {
      return {
        ...state,
        modal: {
          ...state.modal,
          isPrioritiesModalOpen: false
        },
        toolbar: {
          ...state.toolbar,
          editMode: {
            ...state.toolbar.editMode,
            canSave: false,
            hasChanges: true
          }
        },
        data: {
          ...state.data,
          newPriorities: action.newPriorities
        }
      };
    }
    case CLOSE_EDIT_PRIORITIES_MODE: {
      return {
        ...state,
        modal: {
          ...state.modal,
          isPrioritiesModalOpen: false
        },
        toolbar: {
          ...state.toolbar,
          editPrioritiesMode: {
            ...state.toolbar.editPrioritiesMode,
            isEnabled: false
          }
        },
        data: {
          ...state.data,
          selectedDates: []
        }
      };
    }
    default: {
      return state;
    }
  }
};

const combinedReducer = combineReducers({
  toolbar,
  data,
  modal
});

export default reduceReducers(combinedReducer, crossSliceReducer);
