import React from 'react';
import { connect } from 'react-redux';
import { Collapse, Card, CardBody, Table } from 'reactstrap';
import {
  LOSSES_LABEL,
  MONTH_LABEL,
  IN_LOSSES_LABEL,
  OUT_LOSSES_LABEL,
  JANUARY,
  FEBRUARY,
  MARCH,
  APRIL,
  MAY,
  JUNE,
  JULY,
  AUGUST,
  SEPTEMBER,
  OCTOBER,
  NOVEMBER,
  DECEMBER,
  RESULT_LABEL,
} from '../../../constants/constants';
import './Losses.css';


const MONTH_NAMES = {
  '01': JANUARY,
  '02': FEBRUARY,
  '03': MARCH,
  '04': APRIL,
  '05': MAY,
  '06': JUNE,
  '07': JULY,
  '08': AUGUST,
  '09': SEPTEMBER,
  '10': OCTOBER, // eslint-disable-line quote-props
  '11': NOVEMBER, // eslint-disable-line quote-props
  '12': DECEMBER, // eslint-disable-line quote-props
  '13': RESULT_LABEL, // eslint-disable-line quote-props
};


class LossesTab extends React.Component {
  renderRows() {
    const { lossesData: data } = this.props;

    if (!data) {
      return null;
    }

    return data.map((item, i) => (
      <tr key={`losses-table-row-${i}`}>
        <th scope="row">{MONTH_NAMES[item[0].substr(5, 2)]}</th>
        <td>{item[1]}</td>
        <td>{item[2]}</td>
      </tr>
    ));
  }

  render() {
    const { show: showLosses } = this.props.lossesTab;
    return (
      <Collapse
        isOpen={showLosses}
        className="losses-collapse"
      >
        <Card>
          <CardBody>
            <h5>{LOSSES_LABEL}</h5>
            <Table>
              <thead>
                <tr>
                  <th>{MONTH_LABEL}</th>
                  <th>{IN_LOSSES_LABEL}</th>
                  <th>{OUT_LOSSES_LABEL}</th>
                </tr>
              </thead>
              <tbody>
                {this.renderRows()}
              </tbody>
            </Table>
          </CardBody>
        </Card>
      </Collapse>
    );
  }
}


const mapStateToProps = state => ({
  lossesTab: state.layout.toolbar.lossesTab,
  lossesData: state.layout.data.lossesData,
});

export default connect(mapStateToProps, null)(LossesTab);
