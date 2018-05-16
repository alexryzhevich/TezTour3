import React from 'react';
import { connect } from 'react-redux';
import classnames from 'classnames';
import { RIEInput as InlineEdit } from 'riek';
import { GoX } from 'react-icons/lib/go';
import { checkInt } from '../../util/validations';
import { PLACE_DEFAULT_VALUE, NIGHTS } from '../../../constants/constants';

const formatDataToChange = (data, value) => {
  const newData = { ...data, value };

  if (data.value === PLACE_DEFAULT_VALUE) {
    return {
      ...newData,
      outOfOrder: true,
      autoChanged: false
    };
  }

  if (data.autoChanged) {
    return {
      ...newData,
      autoChanged: false
    };
  }

  return {
    ...newData,
    required: true
  };
};

const formatDataToReset = (data) => {
  const newData = {
    ...data,
    required: false
  };

  if (data.outOfOrder) {
    return {
      ...newData,
      outOfOrder: false,
      value: PLACE_DEFAULT_VALUE
    };
  }

  return newData;
};

const formatPassedDaysTitle = passedDays => `${passedDays} ${NIGHTS}`;

class Cell extends React.Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
    this.handleReset = this.handleReset.bind(this);
    this.getPlacesNumberCellClasses = this.getPlacesNumberCellClasses.bind(this);
    this.renderPlacesNumberCell = this.renderPlacesNumberCell.bind(this);
  }

  getPlacesNumberCellClasses() {
    const {
      diagonal,
      required,
      value,
      editable,
      inAmount,
      outOfOrder,
      autoChanged
    } = this.props.data;

    if (outOfOrder) {
      return classnames({
        'editable-td': editable,
        'out-of-order-td': outOfOrder,
        'auto-changed-td': autoChanged
      });
    }

    const less5Pct = value !== PLACE_DEFAULT_VALUE && !diagonal && value <= (inAmount * 0.05);

    return classnames({
      'editable-td': editable,
      'precomputed-td': !required,
      'less-5-pct': less5Pct
    });
  }

  handleReset() {
    const { data, update } = this.props;

    const cellInfo = formatDataToReset(data);
    update(cellInfo);
  }

  handleChange({ value }) {
    const { data, update, validate } = this.props;
    const { rowIndex, columnIndex } = data;

    const safeValue = Number(value);
    if (validate(rowIndex, columnIndex, safeValue)) {
      const cellInfo = formatDataToChange(data, safeValue);
      update(cellInfo);
    } else {
      this.forceUpdate();
    }
  }

  renderPlacesNumberCell() {
    const { data } = this.props;
    const {
      required,
      outOfOrder,
      value,
      passedDays
    } = data;
    const divClass = this.getPlacesNumberCellClasses();

    const props = {
      input: {
        value,
        propName: 'value',
        change: this.handleChange,
        validate: checkInt
      },
      reset: {
        className: 'reset-icon',
        onClick: this.handleReset
      }
    };

    const withCross = required || outOfOrder;

    return (
      <div
        className={divClass}
        title={formatPassedDaysTitle(passedDays)}
      >
        <InlineEdit {...props.input} />
        {
          withCross && <GoX {...props.reset} />
        }
      </div>
    );
  }

  render() {
    const { isEditModeEnabled, isEditPrioritiesModeEnabled, data } = this.props;
    const { value, passedDays } = data;

    // TODO revise to use selector
    const isEditable = isEditModeEnabled && !isEditPrioritiesModeEnabled;

    return isEditable
      ? this.renderPlacesNumberCell()
      : (
        <div
          className={this.getPlacesNumberCellClasses()}
          title={formatPassedDaysTitle(passedDays)}
        >
          { value }
        </div>
      );
  }
}

const mapStateToProps = state => ({
  isEditModeEnabled: state.layout.toolbar.editMode.isEnabled,
  isEditPrioritiesModeEnabled: state.layout.toolbar.editPrioritiesMode.isEnabled
});

export default connect(mapStateToProps)(Cell);
