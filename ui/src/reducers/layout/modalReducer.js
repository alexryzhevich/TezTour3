import {
  TOGGLE_PRIORITIES_MODAL,
  TOGGLE_LOSSES_MODAL,
  TOGGLE_UPDATE_FROM_FILE_MODAL
} from '../../constants/actions/layout';

const setDateType = dateType => ((dateType === 'in' || dateType === 'out') ? dateType : null);

const initialState = {
  isPrioritiesModalOpen: false,
  isUpdateFromFileModalOpen: false,
  losses: {
    isOpen: false
  }
};

const reduce = (state = initialState, action) => {
  switch (action.type) {
    case TOGGLE_UPDATE_FROM_FILE_MODAL: {
      return {
        ...state,
        isUpdateFromFileModalOpen: !state.isUpdateFromFileModalOpen
      };
    }
    case TOGGLE_PRIORITIES_MODAL: {
      return {
        ...state,
        isPrioritiesModalOpen: !state.isPrioritiesModalOpen
      };
    }
    case TOGGLE_LOSSES_MODAL: {
      return {
        ...state,
        losses: {
          ...state.losses,
          isOpen: !state.losses.isOpen,
          dateType: setDateType(action.dateType)
        }
      };
    }
    default: {
      return state;
    }
  }
};

export default reduce;
