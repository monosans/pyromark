use pyo3::{prelude::*, BoundObject};

pub(crate) struct SerdeValueWrapper(pub(crate) serde_json::Value);

impl<'py> IntoPyObject<'py> for SerdeValueWrapper {
    type Error = std::convert::Infallible;
    type Output = Bound<'py, Self::Target>;
    type Target = PyAny;

    fn into_pyobject(
        self,
        py: Python<'py>,
    ) -> Result<Self::Output, Self::Error> {
        match self.0 {
            serde_json::Value::Null => Ok(py.None().into_bound(py).into_any()),
            serde_json::Value::Bool(b) => {
                Ok(b.into_pyobject(py)?.into_bound().into_any())
            }
            serde_json::Value::Number(n) => {
                if let Some(i) = n.as_i64() {
                    Ok(i.into_pyobject(py)?.into_any())
                } else if let Some(u) = n.as_u64() {
                    Ok(u.into_pyobject(py)?.into_any())
                } else if let Some(f) = n.as_f64() {
                    Ok(f.into_pyobject(py)?.into_any())
                } else {
                    unreachable!()
                }
            }
            serde_json::Value::String(s) => Ok(s.into_pyobject(py)?.into_any()),
            serde_json::Value::Array(arr) => Ok(pyo3::types::PyTuple::new(
                py,
                arr.into_iter()
                    .map(move |v| SerdeValueWrapper(v).into_pyobject(py))
                    .collect::<Result<Vec<_>, _>>()?,
            )
            .unwrap()
            .into_any()),
            serde_json::Value::Object(obj) => Ok(
                // Return tuple instead of a dict if dict contains one key
                if obj.len() == 1 {
                    let (k, v) = obj.into_iter().next().unwrap();
                    pyo3::types::PyTuple::new(
                        py,
                        &[
                            k.into_pyobject(py)?.into_any(),
                            SerdeValueWrapper(v).into_pyobject(py)?,
                        ],
                    )
                    .unwrap()
                    .into_any()
                } else {
                    let py_dict = pyo3::types::PyDict::new(py);
                    for (k, v) in obj {
                        py_dict
                            .set_item(
                                k,
                                SerdeValueWrapper(v).into_pyobject(py)?,
                            )
                            .unwrap();
                    }
                    py_dict.into_any()
                },
            ),
        }
    }
}
