//
//  ReportCardScoreBreakdownTableViewCell.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-08.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit


enum ExerciseType {
	case mileRun
	case fourtyYardDash
	case benchPress
	case deadlift
	case squat
	case militaryPress
	
	
	var indicatorColor: UIColor {
		get {
			switch self {
			case .mileRun:
				return UIColor.white
			case .fourtyYardDash:
				return UIColor(red: (243 / 255), green: (71 / 255), blue: (57 / 255), alpha: 1)
			case .benchPress:
				return UIColor(red: (23 / 255), green: (249 / 255), blue: (255 / 255), alpha: 1)
			case .deadlift:
				return UIColor(red: (255 / 255), green: (255 / 255), blue: (0 / 255), alpha: 1)
			case .squat:
				return UIColor(red: (222 / 255), green: (54 / 255), blue: (232 / 255), alpha: 1)
			case .militaryPress:
				return UIColor(red: (255 / 255), green: (0 / 255), blue: (91 / 255), alpha: 1)
			}
		}
	}
}


class ReportCardScoreBreakdownTableViewCell: UITableViewCell {
	
	@IBOutlet fileprivate var privacyContainerView: UIView!
	@IBOutlet fileprivate var isPublicSwitch: UISwitch!
	
	@IBOutlet fileprivate var reportCardView: UIView!
	
	@IBOutlet fileprivate var athleteImageView: UIImageView!
	
	@IBOutlet fileprivate var mileRunGradeIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var mileRunGradeBodyIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var mileRunGradeBodyIndicatorViewFemale: ReportCardIndicatorView!
	@IBOutlet fileprivate var mileRunGradeTitleLabel: UILabel!
	@IBOutlet fileprivate var mileRunGradeLabel: UILabel!
	
	@IBOutlet fileprivate var fourtyYardDashGradeIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var fourtyYardDashGradeBodyIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var fourtyYardDashGradeBodyIndicatorViewFemale: ReportCardIndicatorView!
	@IBOutlet fileprivate var fourtyYardDashGradeTitleLabel: UILabel!
	@IBOutlet fileprivate var fourtyYardDashGradeLabel: UILabel!
	
	@IBOutlet fileprivate var benchPressGradeIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var benchPressGradeBodyIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var benchPressGradeBodyIndicatorViewFemale: ReportCardIndicatorView!
	@IBOutlet fileprivate var benchPressGradeTitleLabel: UILabel!
	@IBOutlet fileprivate var benchPressGradeLabel: UILabel!
	
	@IBOutlet fileprivate var deadliftGradeIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var deadliftGradeBodyIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var deadliftGradeBodyIndicatorViewFemale: ReportCardIndicatorView!
	@IBOutlet fileprivate var deadliftGradeTitleLabel: UILabel!
	@IBOutlet fileprivate var deadliftGradeLabel: UILabel!
	
	@IBOutlet fileprivate var squatGradeIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var squatGradeBodyIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var squatGradeBodyIndicatorViewFemale: ReportCardIndicatorView!
	@IBOutlet fileprivate var squatGradeTitleLabel: UILabel!
	@IBOutlet fileprivate var squatGradeLabel: UILabel!
	
	@IBOutlet fileprivate var militaryPressGradeIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var militaryPressGradeBodyIndicatorView: ReportCardIndicatorView!
	@IBOutlet fileprivate var militaryPressGradeBodyIndicatorViewFemale: ReportCardIndicatorView!
	@IBOutlet fileprivate var militaryPressGradeTitleLabel: UILabel!
	@IBOutlet fileprivate var militaryPressGradeLabel: UILabel!
	
	
	@IBAction private func changedProfileVisibility(_ sender: Any?) {
		guard let visibilitySwitch = sender as? UISwitch, visibilitySwitch == self.isPublicSwitch else {
			return
		}
		
		self.changeProfileVisibility?(visibilitySwitch.isOn)
	}
    
    @IBAction func updateProfileImagePressed(_ sender: Any) {
        self.updateProfileImage?()
    }
	
	fileprivate var lines: [CALayer] = []
	
	
	var isPersonal: Bool = true {
		didSet {
			self.privacyContainerView.isHidden = (self.isPersonal == false)
		}
	}
	
	var isMale: Bool = true {
		didSet {
			self.athleteImageView?.image = self.isMale ? UIImage(named: "ReportCardAthleteMale") : UIImage(named: "ReportCardAthleteFemale")
		}
	}
	
	var reportCard: ReportCard? {
		didSet {
			self.configureViews()
			self.configureLineView()
		}
	}
	
	var isPublic: Bool = false {
		didSet {
			self.isPublicSwitch.setOn(self.isPublic, animated: false)
		}
	}
	
	fileprivate var genderBasedMileRunBodyIndicatorView: ReportCardIndicatorView {
		get {
			return self.isMale ? self.mileRunGradeBodyIndicatorView : self.mileRunGradeBodyIndicatorViewFemale
		}
	}
	
	fileprivate var genderBasedFourtyYardDashBodyIndicatorView: ReportCardIndicatorView {
		get {
			return self.isMale ? self.fourtyYardDashGradeBodyIndicatorView : self.fourtyYardDashGradeBodyIndicatorViewFemale
		}
	}
	
	fileprivate var genderBasedBenchPressBodyIndicatorView: ReportCardIndicatorView {
		get {
			return self.isMale ? self.benchPressGradeBodyIndicatorView : self.benchPressGradeBodyIndicatorViewFemale
		}
	}
	
	fileprivate var genderBasedDeadliftBodyIndicatorView: ReportCardIndicatorView {
		get {
			return self.isMale ? self.deadliftGradeBodyIndicatorView : self.deadliftGradeBodyIndicatorViewFemale
		}
	}
	
	fileprivate var genderBasedSquatBodyIndicatorView: ReportCardIndicatorView {
		get {
			return self.isMale ? self.squatGradeBodyIndicatorView : self.squatGradeBodyIndicatorViewFemale
		}
	}
	
	fileprivate var genderBasedMilitaryPressBodyIndicatorView: ReportCardIndicatorView {
		get {
			return self.isMale ? self.militaryPressGradeBodyIndicatorView : self.militaryPressGradeBodyIndicatorViewFemale
		}
	}
	
	var changeProfileVisibility: ((Bool)->())?
    var updateProfileImage: (()->())?
	
	
	override func awakeFromNib() {
		super.awakeFromNib()
		
	}
	
	override func prepareForReuse() {
		self.isPersonal = false
		self.reportCard = nil
		self.isPublic = false
		
		super.prepareForReuse()
	}
	
	
	func createReportCard() -> UIImage? {
		return self.reportCardView.snapshot(backgroundColor: UIColor(named: .rePerformanceBlue))
	}
	
	
	private func configureViews() {
		guard let reportCard = self.reportCard else {
			return
		}
		
		self.configureViewsGrade(grade: reportCard.mileRunGrade, startDot: self.mileRunGradeIndicatorView, endDot: self.genderBasedMileRunBodyIndicatorView, gradeLabel: self.mileRunGradeLabel, titleLabel: self.mileRunGradeTitleLabel, color: ExerciseType.mileRun.indicatorColor)
		self.configureViewsGrade(grade: reportCard.fourtyYardDashGrade, startDot: self.fourtyYardDashGradeIndicatorView, endDot: self.genderBasedFourtyYardDashBodyIndicatorView, gradeLabel: self.fourtyYardDashGradeLabel, titleLabel: self.fourtyYardDashGradeTitleLabel, color: ExerciseType.fourtyYardDash.indicatorColor)
		self.configureViewsGrade(grade: reportCard.benchPressGrade, startDot: self.benchPressGradeIndicatorView, endDot: self.genderBasedBenchPressBodyIndicatorView, gradeLabel: self.benchPressGradeLabel, titleLabel: self.benchPressGradeTitleLabel, color: ExerciseType.benchPress.indicatorColor)
		self.configureViewsGrade(grade: reportCard.deadliftGrade, startDot: self.deadliftGradeIndicatorView, endDot: self.genderBasedDeadliftBodyIndicatorView, gradeLabel: self.deadliftGradeLabel, titleLabel: self.deadliftGradeTitleLabel, color: ExerciseType.deadlift.indicatorColor)
		self.configureViewsGrade(grade: reportCard.squatGrade, startDot: self.squatGradeIndicatorView, endDot: self.genderBasedSquatBodyIndicatorView, gradeLabel: self.squatGradeLabel, titleLabel: self.squatGradeTitleLabel, color: ExerciseType.squat.indicatorColor)
		self.configureViewsGrade(grade: reportCard.militaryPressGrade, startDot: self.militaryPressGradeIndicatorView, endDot: self.genderBasedMilitaryPressBodyIndicatorView, gradeLabel: self.militaryPressGradeLabel, titleLabel: self.militaryPressGradeTitleLabel, color: ExerciseType.militaryPress.indicatorColor)
	}
	
	private func configureViewsGrade(grade: String?, startDot: ReportCardIndicatorView?, endDot: ReportCardIndicatorView?, gradeLabel: UILabel?, titleLabel: UILabel?, color: UIColor) {
		var gradeText: String = "N/A"
		var textColor: UIColor = .lightGray
		var fillColor: UIColor = .lightGray
		
		if let grade = grade {
			gradeText = grade
			textColor = .white
			fillColor = color
			
			endDot?.alpha = 1
			endDot?.addCircleDashedBorder(fillColor: fillColor)
		}
		else {
			endDot?.alpha = 0
		}
		
		startDot?.addCircleDashedBorder(fillColor: fillColor)
		
		gradeLabel?.text = gradeText
		gradeLabel?.textColor = textColor
		titleLabel?.textColor = textColor
	}
	
	private func configureLineView() {
		self.lines.forEach({ $0.removeFromSuperlayer()} )
		self.lines = []
		
		guard let reportCard = self.reportCard else {
			return
		}
		
		if reportCard.mileRunGrade != nil {
			let line = self.reportCardView.addDashline(startView: self.mileRunGradeIndicatorView, endView: self.genderBasedMileRunBodyIndicatorView, color: ExerciseType.mileRun.indicatorColor)
			self.lines.append(line)
		}
		
		if reportCard.fourtyYardDashGrade != nil {
			let line = self.reportCardView.addDashline(startView: self.fourtyYardDashGradeIndicatorView, endView: self.genderBasedFourtyYardDashBodyIndicatorView, color: ExerciseType.fourtyYardDash.indicatorColor)
			self.lines.append(line)
		}
		
		if reportCard.benchPressGrade != nil {
			let line = self.reportCardView.addDashline(startView: self.benchPressGradeIndicatorView, endView: self.genderBasedBenchPressBodyIndicatorView, color: ExerciseType.benchPress.indicatorColor)
			self.lines.append(line)
		}
		
		if reportCard.deadliftGrade != nil {
			let line = self.reportCardView.addDashline(startView: self.deadliftGradeIndicatorView, endView: self.genderBasedDeadliftBodyIndicatorView, color: ExerciseType.deadlift.indicatorColor)
			self.lines.append(line)
		}
		
		if reportCard.squatGrade != nil {
			let line = self.reportCardView.addDashline(startView: self.squatGradeIndicatorView, endView: self.genderBasedSquatBodyIndicatorView, color:ExerciseType.squat.indicatorColor)
			self.lines.append(line)
		}
		
		if reportCard.militaryPressGrade != nil {
			let line = self.reportCardView.addDashline(startView: self.militaryPressGradeIndicatorView, endView: self.genderBasedMilitaryPressBodyIndicatorView, color: ExerciseType.militaryPress.indicatorColor)
			self.lines.append(line)
		}
	}
}
