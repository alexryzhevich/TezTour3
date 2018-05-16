import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import isNil from 'lodash/isNil';
import { Modal, ModalBody } from 'reactstrap';
import LossesForm from '../../form/losses';
import { toggleLossesModal } from '../../../actions/layout';

const formatDate = date => new Date(date).toLocaleDateString('ru-RU');

const retrieveDatesByType = (dates, type) => {
  switch (type) {
    case 'in': return dates
      .map(date => date.inDate)
      .filter(date => !isNil(date));
    case 'out': return dates
      .map(date => date.outDate)
      .filter(date => !isNil(date));
    default: return [];
  }
};

const retrieveNoLossesIntervals = (dates, type) => {
  const intervals = [];
  let startDate = null;
  let endDate = null;
  const dateName = type === 'in' ? 'inDate' : 'outDate';
  const noLossesName = type === 'in' ? 'inNoLosses' : 'outNoLosses';
  for (let i = 0; i < dates.length; i += 1) {
    if (isNil(dates[i][dateName])) {
      continue;
    }
    if (dates[i][noLossesName] && !!startDate) {
      endDate = formatDate(dates[i][dateName]);
    }
    if (dates[i][noLossesName] && !startDate) {
      startDate = formatDate(dates[i][dateName]);
      endDate = formatDate(dates[i][dateName]);
    }
    if (!dates[i][noLossesName] && !!startDate) {
      intervals.push({ startDate, endDate });
      startDate = null;
      endDate = null;
    }
  }
  if (startDate) {
    intervals.push({ startDate, endDate });
  }
  return intervals;
};


const convertIntervalsToNoLosses = (dates, type, intervals) => {
  const dateName = type === 'in' ? 'inDate' : 'outDate';
  const findIndex = date => dates.findIndex(el => el[dateName] && formatDate(el[dateName]) === date);
  const idxIntervals = intervals.map(int => ({ startDate: findIndex(int.startDate), endDate: findIndex(int.endDate) }));
  const noLosses = dates.map(() => [false, false]);
  for (let i = 0; i < dates.length; i += 1) {
    if (!dates[i][dateName]) {
      continue;
    }
    noLosses[i][type === 'in' ? 1 : 0] = dates[i][type === 'in' ? 'outNoLosses' : 'inNoLosses'];
    for (let j = 0; j < idxIntervals.length; j += 1) {
      if (i >= idxIntervals[j].startDate && i <= idxIntervals[j].endDate) {
        noLosses[i][type === 'in' ? 0 : 1] = true;
        break;
      }
    }
  }
  return noLosses;
};


class LossesModal extends React.PureComponent {
  constructor(props) {
    super(props);

    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleSubmit(intervals) {
    const {
      dates, lossesModal, toggleLossesModal, onSubmit
    } = this.props;
    const { dateType } = lossesModal;
    const noLosses = convertIntervalsToNoLosses(dates, dateType, intervals);
    toggleLossesModal();
    onSubmit(noLosses);
  }

  render() {
    const {
      dates, lossesModal, toggleLossesModal
    } = this.props;
    const { isOpen, dateType } = lossesModal;

    const datesByType = retrieveDatesByType(dates, dateType);
    const noLossesIntervals = retrieveNoLossesIntervals(dates, dateType);

    return (
      <Modal isOpen={isOpen} toggle={toggleLossesModal}>
        <ModalBody>
          <LossesForm
            dates={datesByType}
            toggle={toggleLossesModal}
            onSubmit={this.handleSubmit}
            intervals={noLossesIntervals}
          />
        </ModalBody>
      </Modal>
    );
  }
}

const mapStateToProps = state => ({
  lossesModal: state.layout.modal.losses,
  dates: state.layout.data.formattedData
});

const mapDispatchToProps = dispatch => bindActionCreators({
  toggleLossesModal
}, dispatch);

export default connect(mapStateToProps, mapDispatchToProps)(LossesModal);
