package org.maltparser.core.feature.value;

import org.maltparser.core.feature.function.Function;
/**
 *  
 *
 * @author Johan Hall
 * @since 1.0
**/
public class SingleFeatureValue extends FeatureValue {
	protected int indexCode;
	protected String symbol;
	protected double value;
	
	public SingleFeatureValue(Function function) {
		super(function);
		setIndexCode(0);
		setSymbol(null);
		setValue(0);
	}
	
	public void reset() {
		super.reset();
		setIndexCode(0);
		setSymbol(null);
		setValue(0);
	}
	
	public void update(int indexCode, String symbol, boolean nullValue, double value) {
		this.indexCode = indexCode;
		this.symbol = symbol;
		this.nullValue = nullValue;
		this.value = value;
	}
	
	public int getIndexCode() {
		return indexCode;
	}

	public void setIndexCode(int code) {
		this.indexCode = code;
	}

	public String getSymbol() {
		return symbol;
	}

	public void setSymbol(String symbol) {
		this.symbol = symbol;
	}

	public double getValue() {
		return value;
	}

	public void setValue(double value) {
		this.value = value;
	}
	
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		SingleFeatureValue v = (SingleFeatureValue)obj;
		if (indexCode != v.indexCode)
			return false;
		if (!symbol.equals(v.symbol))
			return false;
		return super.equals(obj);
	}
	
	public String toString() {
		StringBuilder sb = new StringBuilder();
		sb.append(super.toString());
		sb.append('{');
		sb.append(symbol);
		sb.append("->");
		sb.append(indexCode);
		sb.append('}');
		return sb.toString();
	}
}
