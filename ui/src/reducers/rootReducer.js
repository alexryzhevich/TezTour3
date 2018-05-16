import { combineReducers } from 'redux';
import { reducer as formReducer } from 'redux-form';
import { routerReducer } from 'react-router-redux';
import layout from './layout';
import ui from './ui';

const rootReducer = combineReducers({
  routing: routerReducer,
  form: formReducer,
  ui,
  layout
});

export default rootReducer;

