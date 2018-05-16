import React from 'react';
import { Input, FormFeedback } from 'reactstrap';
import './Priorities.css';

const isNumber = val => '0123456789'.indexOf(val) !== -1;

const getPercent = (len, val) => (len === 2 && val[0] === '0' ? val[1] : val);

const removeLastSymbol = (len, val) => (len === 1 ? '0' : val.substring(0, len - 1));

const getNumberValue = (val) => {
  const len = val.length;
  if (len === 4 || (len === 3 && isNumber(val[len - 1]))) {
    return '100';
  }
  return isNumber(val[len - 1]) ? getPercent(len, val) : removeLastSymbol(len, val);
};

const getValue = value => value || '';

class PrioritiesInput extends React.Component {
  constructor(props) {
    super(props);

    this.onChange = this.onChange.bind(this);
  }

  onChange(props) {
    return (event) => {
      props.onChange(getNumberValue(event.target.value));
    };
  }

  render() {
    const {
      typeValue, input, label, meta: { touched, error }, ...custom
    } = this.props;

    const props = {
      placeholder: label,
      ...(touched && error) && {
        valid: false,
      },
      ...input,
      ...custom,
    };

    return (
      <span>
        <Input
          {...props}
          value={getValue(props.value)}
          onChange={this.onChange(props)}
          className="custom-input"
        />
        <span className="value-type">{typeValue}</span>
        <FormFeedback>{error}</FormFeedback>
      </span>
    );
  }
}

export default PrioritiesInput;
