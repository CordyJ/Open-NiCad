class EmailValidator < ActiveModel::EachValidator
  def validate_each(record, attribute, value)
    warn "`EmailValidator` in 'lib/spree/core' is deprecated. Use `EmailValidator` in 'app/validators' instead."
    unless value =~ /\A[^@\s]+@[^@\s]+\z/
      record.errors.add(attribute, :invalid, { value: value }.merge!(options))
    end
  end
end
