//
//  LeaderboardSelectionViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-29.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


protocol LeaderboardSelectionCell {
	var titleText:String { get }
	var exerciseTestFormat:ExerciseTestFormat? { get }
}


struct GlobalLeaderboardSelectionCell: LeaderboardSelectionCell {
	
	let titleText: String = Constants.ReportCard.GlobalLeaderboardSelectionCellTitleText
	let exerciseTestFormat: ExerciseTestFormat? = nil
}


struct LeaderboardSelectionCellData: LeaderboardSelectionCell {
	
	let titleText: String
	let exerciseTestFormat: ExerciseTestFormat?
	
	
	init(exerciseTestFormat: ExerciseTestFormat) {
		self.exerciseTestFormat = exerciseTestFormat
		self.titleText = LeaderboardSelectionCellData.textForExerciseFormat(exerciseTestFormat)
	}
	
	
	static func textForExerciseFormat(_ exerciseFormat:ExerciseTestFormat) -> String {
		switch exerciseFormat {
		case .TrackRunning:
			return L10n.trackRunning
		case .Outdoor:
			return L10n.outdoor
		case .Treadmill:
			return L10n.treadmill
		case .SelfTimed:
			return L10n.selfTimed
		case .CuedTime:
			return L10n.cuedTime
		case .Stamina:
			return L10n.stamina
		case .Endurance:
			return L10n.endurance
		case .Strength:
			return L10n.strength
		case .Power:
			return L10n.power
		}
	}
}


protocol LeaderboardSelectionHeader {
	var exerciseType: Array<LeaderboardSelectionCell> { get }
	var exerciseCategory: ExerciseCategory? { get }
}


struct GlobalLeaderboardSelectionHeader:LeaderboardSelectionHeader {
	
	let exerciseType: Array<LeaderboardSelectionCell> = [GlobalLeaderboardSelectionCell()]
	let exerciseCategory: ExerciseCategory? = nil
}


struct LeaderboardSelectionHeaderData: LeaderboardSelectionHeader {
	
	let exerciseCategory: ExerciseCategory?
	let exerciseCategoryTitle: String
	let exerciseCategoryImage: UIImage
	let exerciseType: Array<LeaderboardSelectionCell>
	
	
	init(exerciseCategory: ExerciseCategory) {
		self.exerciseCategory = exerciseCategory
		self.exerciseCategoryTitle = LeaderboardSelectionHeaderData.titleForExerciseCategory(exerciseCategory: exerciseCategory)
		self.exerciseCategoryImage = LeaderboardSelectionHeaderData.imageForExerciseCategory(exerciseCategory: exerciseCategory)
		self.exerciseType = LeaderboardSelectionHeaderData.testFormatsForExerciseCategory(exerciseCategory: exerciseCategory)
	}
	
	
	static func titleForExerciseCategory(exerciseCategory:ExerciseCategory) -> String {
		switch exerciseCategory {
		case .MileRun:
			return L10n.testInformationMileRunTitle
		case .FortyYardDash:
			return L10n.testInformationYardDashTitle
		case .BenchPress:
			return L10n.testInformationBenchPressTitle
		case .DeadLift:
			return L10n.testInformationDeadliftTitle
		case .Squat:
			return L10n.testInformationSquatTitle
		case .MilitaryPress:
			return L10n.testInformationMilitaryPressTitle
		}
	}
	
	static func imageForExerciseCategory(exerciseCategory:ExerciseCategory) -> UIImage{
		switch exerciseCategory {
		case .MileRun:
			return #imageLiteral(resourceName: "ScoreHeaderMileRun")
		case .FortyYardDash:
			return #imageLiteral(resourceName: "ScoreHeaderFortyYardDash")
		case .BenchPress:
			return #imageLiteral(resourceName: "ScoreHeaderBenchPress")
		case .DeadLift:
			return #imageLiteral(resourceName: "ScoreHeaderDeadlift")
		case .Squat:
			return #imageLiteral(resourceName: "ScoreHeaderSquat")
		case .MilitaryPress:
			return #imageLiteral(resourceName: "ScoreHeaderMilitaryPress")
		}
	}
	
	static func testFormatsForExerciseCategory(exerciseCategory:ExerciseCategory) -> Array<LeaderboardSelectionCellData>{
		switch exerciseCategory {
		case .MileRun:
			return LeaderboardSelectionHeaderData.LeaderboardSelectionCellDataForExerciseCategories([.TrackRunning, .Outdoor, .Treadmill])
		case .FortyYardDash:
			return LeaderboardSelectionHeaderData.LeaderboardSelectionCellDataForExerciseCategories([.SelfTimed, .CuedTime])
		case .BenchPress, .DeadLift, .Squat, .MilitaryPress:
			return LeaderboardSelectionHeaderData.LeaderboardSelectionCellDataForExerciseCategories([.Stamina, .Endurance, .Strength, .Power])
		}
	}
	
	static func LeaderboardSelectionCellDataForExerciseCategories(_ exerciseFormats:Array<ExerciseTestFormat>) -> Array<LeaderboardSelectionCellData>{
		var arrayToReturn:Array<LeaderboardSelectionCellData> = []
		for format in exerciseFormats {
			arrayToReturn.append(LeaderboardSelectionCellData(exerciseTestFormat: format))
		}
		
		return arrayToReturn
	}
}


struct LeaderboardSelectionViewData {
	
	var exerciseCategories: Array<LeaderboardSelectionHeader>
	
	init() {
		var localArray: Array<LeaderboardSelectionHeader> = [GlobalLeaderboardSelectionHeader()]
		let categories: Array<ExerciseCategory> = [.MileRun, .FortyYardDash, .BenchPress, .DeadLift, .Squat, .MilitaryPress]
		for category in categories {
			localArray.append(LeaderboardSelectionHeaderData(exerciseCategory: category))
		}
		self.exerciseCategories = localArray
	}
}


class LeaderboardSelectionViewController: UIViewController {
	
	@IBOutlet private var tableView: UITableView?
	@IBOutlet private var informationLabel: UILabel?
	
	var isGymType: Bool = false
	var viewData: LeaderboardSelectionViewData = LeaderboardSelectionViewData()
	var exerciseCategory: ExerciseCategory?
	
	var cancel: (()->())?
	var selectionMade: ((ExerciseCategory?, ExerciseTestFormat?)->())?
	var changeGym: (()->())?
	
	
	override func viewDidLoad() {
		super.viewDidLoad()
		
		self.tableView?.estimatedRowHeight = 44
		self.tableView?.rowHeight = UITableView.automaticDimension
		self.navigationItem.rightBarButtonItem = UIBarButtonItem(image: Asset.Assets.changeGymIcon.image, style: .plain, target: self, action: #selector(changeGymTapped(_:)))
	}
	
	
	@objc func changeGymTapped(_ sender: UIButton?) {
		self.changeGym?()
	}
	
	func setUpView() {
		if self.isGymType {
			self.title = L10n.gymLeaderboardTitle
			self.informationLabel?.text = L10n.gymLeaderboardInformationText
			self.viewData.exerciseCategories.removeFirst()
		} else {
			self.title = L10n.testLeaderboardTitle
			self.informationLabel?.text = L10n.testLeaderboardInformationText
			self.navigationItem.leftBarButtonItem = UIBarButtonItem(barButtonSystemItem: .cancel, target: self, action: #selector(dismissTapped(_:)))
		}
		
		self.informationLabel?.textColor = UIColor.white
	}
	
	@IBAction private func dismissTapped(_ sender: UIButton) {
		self.cancel?()
	}
}


extension LeaderboardSelectionViewController: UITableViewDataSource, UITableViewDelegate {
	
	func numberOfSections(in tableView: UITableView) -> Int {
		return self.viewData.exerciseCategories.count
	}
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
		return self.viewData.exerciseCategories[section].exerciseType.count
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		let defaultCell = UITableViewCell.init(style: .default, reuseIdentifier: "default")
		defaultCell.textLabel?.text = "Error"
		
		guard let cell = tableView.dequeueReusableCell(withIdentifier: Constants.ReportCard.LeaderboardSelectionCell, for: indexPath) as? LeaderboardSelectionTableViewCell else {
			return defaultCell
		}
		
		cell.setExerciseTestTypeLabelWithText(self.viewData.exerciseCategories[indexPath.section].exerciseType[indexPath.row].titleText)
		
		return cell
	}
	
	func tableView(_ tableView: UITableView, viewForHeaderInSection section: Int) -> UIView? {
		let defaultCell = UITableViewCell.init(style: .default, reuseIdentifier: "default")
		defaultCell.textLabel?.text = "Error"
		
		if let headerData = self.viewData.exerciseCategories[section] as? LeaderboardSelectionHeaderData {
			guard let cell = tableView.dequeueReusableCell(withIdentifier: Constants.ReportCard.LeaderboardSelectionHeaderCell) as? LeaderboardSelectionHeaderTableViewCell else {
				return defaultCell
			}
			
			cell.configureCell(exerciseCategoryText: headerData.exerciseCategoryTitle, exerciseCategoryImage: headerData.exerciseCategoryImage)
			
			return cell
		}
		else {
			return nil
		}
	}
	
	func tableView(_ tableView: UITableView, heightForHeaderInSection section: Int) -> CGFloat {
		if self.viewData.exerciseCategories[section] is LeaderboardSelectionHeaderData{
			return Constants.ReportCard.LeaderboardSelectionHeaderCellHeight
		}
		else {
			return 0
		}
	}
	
	func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
		let selectedExerciseCategory = self.viewData.exerciseCategories[indexPath.section]
		let exerciseCategory = selectedExerciseCategory.exerciseCategory
		let exerciseTestFormat = selectedExerciseCategory.exerciseType[indexPath.row].exerciseTestFormat
		
		self.selectionMade?(exerciseCategory, exerciseTestFormat)
	}
}
