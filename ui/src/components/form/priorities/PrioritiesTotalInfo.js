import React from 'react';
import range from 'lodash/range';
import { Label, FormGroup, Col } from 'reactstrap';
import { Field } from 'redux-form';

import renderPrioritiesInput from '../utils/renderPrioritiesInput';
import PrioritiesDescription from '../utils/PrioritiesDescription';

import { DAYS } from '../../../constants/constants';

class PrioritiesTotalInfo extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      priorities: props.priorities ? props.priorities : []
    };
    this.initialize = this.initialize.bind(this);
  }

  componentDidMount() {
    const { minDays, maxDays } = this.props;
    this.initialize(minDays, maxDays);
  }

  initialize(minDays, maxDays) {
    const { fields } = this.props;
    const { priorities } = this.state;
    const count = priorities ? priorities.length : (Number(maxDays) - Number(minDays)) + 1;
    fields.removeAll();
    range(0, count).forEach(index => fields.push(priorities ? priorities[index] : null));
  }

  render() {
    const { fields, minDays, description } = this.props;
    const priorities = fields.map((item, index) => {
      const dayNumber = Number(minDays) + index;
      const label = `${dayNumber} ${DAYS}`;
      return (
        <FormGroup
          key={index}
          row
        >
          <Label for="name" sm={3}>
            { label }
          </Label>
          <Col sm={3}>
            <Field name={`priorities[${index}]`} type="text" component={renderPrioritiesInput} placeholder="%" typeValue="%" />
          </Col>
        </FormGroup>
      );
    });
    return (
      <div className="priorities-total-info">
        <PrioritiesDescription priorities={fields.getAll()} description={description} />
        { priorities }
      </div>
    );
  }
}

export default PrioritiesTotalInfo;
