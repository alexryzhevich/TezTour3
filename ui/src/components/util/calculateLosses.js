
function getMonthFromDate(date) {
  return date.substr(0, 7);
}


function addEmptyLine(monthIdx, idxMapping, result, month) {
  if (!idxMapping[month] && idxMapping[month] !== 0) {
    result.push([month, 0, 0]);
    idxMapping[month] = monthIdx;
    return monthIdx + 1;
  }
  return monthIdx;
}

function addResultLosses(result) {
  let resInLosses = 0;
  let resOutLosses = 0;
  result.forEach((item) => {
    resInLosses += item[1];
    resOutLosses += item[2];
  });
  result.push(['xxxx-13', resInLosses, resOutLosses]);
}


export function calculateLosses(formattedData) {
  let months = 0;
  const res = [];
  const idxMapping = {};
  formattedData.forEach((item) => {
    if (item.inDate) {
      const inMonth = getMonthFromDate(item.inDate);
      months = addEmptyLine(months, idxMapping, res, inMonth);
      res[idxMapping[inMonth]][1] += item.inLosses;
    }
    if (item.outDate) {
      const outMonth = getMonthFromDate(item.outDate);
      months = addEmptyLine(months, idxMapping, res, outMonth);
      res[idxMapping[outMonth]][2] += item.outLosses;
    }
  });
  addResultLosses(res);
  return res;
}
